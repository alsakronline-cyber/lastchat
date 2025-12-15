(function($) {
    $(document).ready(function() {
        const apiUrl = industrialAI.apiUrl;

        // 1. Inject Styles dynamically (or use widget.css)
        const styles = `
            #ia-chat-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 350px;
                height: 500px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                display: none;
                flex-direction: column;
                z-index: 9999;
                font-family: 'Segoe UI', sans-serif;
                overflow: hidden;
            }
            #ia-chat-header {
                background: #0073aa;
                color: white;
                padding: 15px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            #ia-chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
                background: #f9f9f9;
            }
            #ia-chat-input-area {
                padding: 10px;
                border-top: 1px solid #eee;
                display: flex;
            }
            #ia-chat-input {
                flex: 1;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-right: 5px;
            }
            #ia-chat-send {
                background: #0073aa;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            #ia-chat-toggle {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #0073aa;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                text-align: center;
                line-height: 60px;
                font-size: 24px;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(0,0,0,0.2);
                z-index: 9999;
            }
            .ia-message {
                margin-bottom: 10px;
                padding: 10px;
                border-radius: 8px;
                max-width: 80%;
            }
            .ia-message.user {
                background: #e1f5fe;
                align-self: flex-end;
                margin-left: auto;
            }
            .ia-message.bot {
                background: white;
                border: 1px solid #eee;
                align-self: flex-start;
            }
            .ia-product-card {
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                margin-top: 5px;
            }
            .ia-product-title {
                font-weight: bold;
                font-size: 14px;
            }
            .ia-product-sku {
                color: #666;
                font-size: 12px;
            }
        `;
        $('<style>').text(styles).appendTo('head');

        // 2. Build UI
        const chatHTML = `
            <div id="ia-chat-toggle">💬</div>
            <div id="ia-chat-container">
                <div id="ia-chat-header">
                    <span>AI Assistant</span>
                    <span id="ia-chat-close" style="cursor:pointer;">✖</span>
                </div>
                <div id="ia-chat-messages">
                    <div class="ia-message bot">Hello! I'm your technical assistant. What product are you looking for?</div>
                </div>
                <div id="ia-chat-input-area">
                    <input type="text" id="ia-chat-input" placeholder="Type your requirements...">
                    <button id="ia-chat-send">Send</button>
                </div>
            </div>
        `;
        $('body').append(chatHTML);

        // 3. Event Listeners
        $('#ia-chat-toggle, #ia-chat-close').click(function() {
            $('#ia-chat-container').toggle();
            $('#ia-chat-toggle').toggle();
            if ($('#ia-chat-container').is(':visible')) {
                $('#ia-chat-input').focus();
            }
        });

        $('#ia-chat-send').click(sendMessage);
        $('#ia-chat-input').keypress(function(e) {
            if (e.which == 13) sendMessage();
        });

        // 4. Logic
        function sendMessage() {
            const query = $('#ia-chat-input').val().trim();
            if (!query) return;

            // Add User Message
            appendMessage('user', query);
            $('#ia-chat-input').val('');

            // Loading indicator
            const loadingId = appendMessage('bot', 'Thinking...');

            // API Call
            $.ajax({
                url: apiUrl + '/recommend',
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ query: query, top_k: 3 }),
                success: function(response) {
                    $(`#${loadingId}`).remove(); // Remove loading
                    
                    let answer = response.answer;
                    
                    // Format sources if available
                    if (response.sources && response.sources.length > 0) {
                        answer += "<hr style='margin:10px 0; border:0; border-top:1px solid #eee;'><strong>Recommended Products:</strong>";
                        response.sources.forEach(src => {
                            answer += `
                                <div class="ia-product-card">
                                    <div class="ia-product-title">${src.name}</div>
                                    <div class="ia-product-sku">SKU: ${src.sku}</div>
                                </div>
                            `;
                        });
                    }
                    
                    appendMessage('bot', answer);
                },
                error: function(err) {
                    $(`#${loadingId}`).remove();
                    appendMessage('bot', 'Sorry, I encountered an error connecting to the server.');
                    console.error(err);
                }
            });
        }

        function appendMessage(sender, text) {
            const id = 'msg-' + new Date().getTime();
            const msgDiv = $(`<div id="${id}" class="ia-message ${sender}"></div>`).html(text);
            $('#ia-chat-messages').append(msgDiv);
            $('#ia-chat-messages').scrollTop($('#ia-chat-messages')[0].scrollHeight);
            return id;
        }
    });
})(jQuery);
