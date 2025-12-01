// ============================================================================
// PART 1: ScoutApi client
// ============================================================================

class ScoutApi {
    constructor(copilotId, environment = 'production') {
        if (!copilotId) {
            throw new Error("ScoutApi: copilotId is required.");
        }
        this.copilotId = copilotId;
        this.environment = environment;
        this.baseUrl = this.environment === 'production'
            ? "https://api-prod.scoutos.com"
            : "https://workflow-service-535536037740.us-central1.run.app";
        this.v1Url = "https://api-prod.scoutos.com";
        this.token = null;
        this.copilotConfig = null;
        this.userId = this._getOrSetUserId();
        this.sessionId = this._generateUniqueId();
    }

    async initialize() {
        await this._fetchToken();
        await this._fetchCopilotConfig();
        return this;
    }

    async sendMessage(message, options = {}) {
        const { stream = true, metadata = {}, chat_history = [] } = options;

        await this._checkToken();

        const workflowId = this.copilotConfig?.workflow_id;
        if (!workflowId) {
            throw new Error("Could not find 'workflow_id' in the fetched copilot configuration.");
        }

        const params = new URLSearchParams({
            copilot_id: this.copilotId,
            session_id: this.sessionId
        });

        const apiUrl = `${this.baseUrl}/v2/copilot/${workflowId}/cook?${params.toString()}`;

        const payload = {
            inputs: {
                user_message: message,
                chat_history: chat_history,
                metadata: metadata
            },
            streaming: stream
        };

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            let errorBody;
            try {
                errorBody = await response.clone().json();
            } catch (e) {
                errorBody = await response.text();
            }
            console.error("API Error Response:", errorBody);
            throw new Error(
                `API request failed with status ${response.status}: ${JSON.stringify(errorBody)}`
            );
        }

        return stream ? response.body : response.json();
    }

    async parseSseStream(stream, onMessage) {
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            let boundary;
            while ((boundary = buffer.indexOf('\n\n')) !== -1) {
                const message = buffer.slice(0, boundary);
                buffer = buffer.slice(boundary + 2);

                const dataLine = message
                    .split('\n')
                    .find(line => line.startsWith('data:'));

                if (dataLine) {
                    const jsonString = dataLine.substring(6);
                    try {
                        const dataObject = JSON.parse(jsonString);
                        if (onMessage) {
                            onMessage(dataObject);
                        }
                    } catch (e) {
                        console.error("Failed to parse SSE data JSON:", jsonString, e);
                    }
                }
            }
        }
    }

    async _fetchToken() {
        try {
            const tokenUrl = `${this.v1Url}/v1/copilot/get-ingredient`;
            const response = await fetch(tokenUrl, { method: "GET" });

            if (!response.ok) {
                throw new Error(`Token fetch failed: ${response.statusText}`);
            }

            const { token } = await response.json();
            this.token = token;
        } catch (error) {
            console.error("Error fetching token:", error);
            throw error;
        }
    }

    async _fetchCopilotConfig() {
        try {
            const configUrl = `${this.baseUrl}/v2/copilots/${this.copilotId}`;
            const response = await fetch(configUrl, { method: "GET" });

            if (!response.ok) {
                throw new Error(`Config fetch failed: ${response.statusText}`);
            }

            const jsonResponse = await response.json();
            this.copilotConfig = jsonResponse.data.copilot_config;
        } catch (error) {
            console.error("Error fetching config:", error);
            throw error;
        }
    }

    async _checkToken() {
        if (!this._isJwtValid(this.token)) {
            console.log("Token expired or invalid, fetching a new one.");
            await this._fetchToken();
        }
    }

    _isJwtValid(token) {
        if (!token) return false;
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            if (!payload || typeof payload.exp !== 'number') return false;
            const isExpired = (Date.now() /1000) >= payload.exp;
            return !isExpired;
        } catch (error) {
            return false;
        }
    }

    _getOrSetUserId() {
        const STORAGE_KEY = "scout_user_id";
        try {
            let userId = localStorage.getItem(STORAGE_KEY);
            if (!userId) {
                userId = this._generateUniqueId();
                localStorage.setItem(STORAGE_KEY, userId);
            }
            return userId;
        } catch (error) {
            console.warn("Could not access localStorage. Using a temporary user ID.");
            return this._generateUniqueId();
        }
    }

    _generateUniqueId() {
        if (window.crypto && window.crypto.randomUUID) {
            return window.crypto.randomUUID();
        }
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
}

// ============================================================================
// PART 2: SAGE Chat Logic (Your UI)
// ============================================================================

// 🔥 YOUR COPILOT ID
const COPILOT_ID = "copilot_cmhwre2zi00010hs6zovbwgah";

let scoutApi = null;
let chatHistory = [];

let chatWindowEl;
let userInputEl;
let sendButtonEl;

// Load script helper (for marked + DOMPurify)
function loadScript(src) {
    return new Promise((resolve, reject) => {
        if (document.querySelector(`script[src="${src}"]`)) {
            resolve();
            return;
        }
        const script = document.createElement("script");
        script.src = src;
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
        document.head.appendChild(script);
    });
}

// Append safe HTML
function addMessageHtml(html, sender) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerHTML = html;
    chatWindowEl.appendChild(div);
    chatWindowEl.scrollTop = chatWindowEl.scrollHeight;
}

// Append plain text
function addMessageText(text, sender) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerText = text;
    chatWindowEl.appendChild(div);
    chatWindowEl.scrollTop = chatWindowEl.scrollHeight;
}

function addThinkingBubble() {
    const div = document.createElement("div");
    div.classList.add("message", "bot");
    div.innerHTML = `<div class="thinking-indicator"><span>.</span><span>.</span><span>.</span></div>`;
    chatWindowEl.appendChild(div);
    chatWindowEl.scrollTop = chatWindowEl.scrollHeight;
    return div;
}

function setUIBusy(isBusy) {
    userInputEl.disabled = isBusy;
    if (isBusy) {
        sendButtonEl.classList.add("disabled");
    } else {
        sendButtonEl.classList.remove("disabled");
        userInputEl.focus();
    }
}

// Main send message
async function handleSendMessage() {
    const message = userInputEl.value.trim();
    if (!message || !scoutApi) return;

    addMessageText(message, "user");

    userInputEl.value = "";
    setUIBusy(true);

    const aiBubble = addThinkingBubble();
    let fullMarkdown = "";

    try {
        const stream = await scoutApi.sendMessage(message, {
            stream: true,
            chat_history: [...chatHistory]
        });

        const handleMessage = (dataObject) => {
            const eventName = dataObject?.event_type;
            const eventData = dataObject?.data;

            if (
                eventName === "block_state_updated" &&
                eventData?.block_id === "copilot_message" &&
                eventData?.update_type === "partial"
            ) {
                const chunk = eventData?.update_data?.output;
                if (chunk) {
                    fullMarkdown += chunk;

                    const raw = marked.parse(fullMarkdown);
                    const safe = DOMPurify.sanitize(raw);
                    aiBubble.innerHTML = safe;

                    chatWindowEl.scrollTop = chatWindowEl.scrollHeight;
                }
            }
        };

        await scoutApi.parseSseStream(stream, handleMessage);

        if (fullMarkdown) {
            chatHistory.push({ role: "human", content: message });
            chatHistory.push({ role: "ai", content: fullMarkdown });
        }

    } catch (error) {
        aiBubble.innerHTML = `<b>Error:</b> ${error.message}`;
    } finally {
        setUIBusy(false);
    }
}

// Make it callable from HTML
function sendMessage() {
    handleSendMessage();
}
window.sendMessage = sendMessage;

// Info popup
function moreInfo() {
    alert(
        "Welcome to SAGE 🎓\n\n" +
        "Ask me about internships, study abroad, or how to use this tool.\n\n" +
        "Examples:\n" +
        "• What internships are available for CS majors?\n" +
        "• When are study abroad deadlines?\n" +
        "• How do I improve my resume?"
    );
}
window.moreInfo = moreInfo;

// Initialize
document.addEventListener("DOMContentLoaded", async () => {
    chatWindowEl = document.getElementById("chat-window");
    userInputEl = document.getElementById("user-input");
    sendButtonEl = document.querySelector(".input-container button");

    setUIBusy(true);

    try {
        await Promise.all([
            loadScript("https://cdn.jsdelivr.net/npm/marked/marked.min.js"),
            loadScript("https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js")
        ]);

        scoutApi = new ScoutApi(COPILOT_ID);
        await scoutApi.initialize();

        addMessageText(
            "Hi, I’m SAGE! Ask me about internships, study abroad, or how to use this tool.",
            "bot"
        );

    } catch (err) {
        addMessageHtml(
            "<b>Error:</b> Unable to initialize SAGE. Check your Copilot ID or network.",
            "bot"
        );
    } finally {
        setUIBusy(false);
    }

    userInputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });
});
