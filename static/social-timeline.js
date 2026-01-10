document.addEventListener("DOMContentLoaded", function() {
    const instance = "https://ttrpg-hangout.social";
    const container = document.getElementById("mastodon-timeline");
    
    // Fetch local timeline, limit to 10 posts
    fetch(`${instance}/api/v1/timelines/public?local=true&limit=10`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = "";
            
            data.forEach(status => {
                // 0. RESPECT PRIVACY:
                // If the user has opted out of indexing/discovery, skip them.
                // (Note: Some instances use 'noindex', some use 'discoverable'. We check both.
                if (status.account.noindex === true || status.account.discoverable === false) {
                    return;
                }
                
                const div = document.createElement("div");
                div.className = "toot-entry";
                
                // 1. OUTER SPACING
                div.style.marginBottom = "10px"; 
                div.style.paddingBottom = "10px";
                div.style.borderBottom = "1px solid #eee";
                
                // 2. CONTENT PREP (Handle CWs and Kill P-tag margins)
                let content = status.content;
                if (status.spoiler_text) {
                    content = `<p style="margin:0;"><strong>CW: ${status.spoiler_text}</strong> <br> 
                               <span style="font-size:0.8rem; color:#666;">(Click to view)</span></p>`;
                } else {
                    // Force all paragraphs to have 0 margin to prevent "Phantom Margins"
                    content = content.replace(/<p>/g, '<p style="margin: 0; margin-bottom: 5px;">');
                }

                div.innerHTML = `
                    <div style="display: flex; 
                                align-items: center; 
                                justify-content: flex-start; 
                                text-align: left;
                                margin-bottom: 5px;">
                        
                        <div style="width: 60px; min-width: 60px; margin-right: 15px;">
                            <img src="${status.account.avatar}" 
                                 style="width: 60px; height: 60px; 
                                        border-radius: 15%; 
                                        display: block; 
                                        margin: 0 !important;
                                        max-width: none;"> 
                        </div>
                        
                        <div style="flex-grow: 1; line-height: 1.2; text-align: left;">
                            <a href="${status.account.url}" style="font-weight: bold; text-decoration: none; color: inherit; font-size: 0.9rem;">
                                ${status.account.display_name}
                            </a>
                        </div>
                    </div>
                    
                    <div style="font-size: 0.9rem; color: #333; text-align: left; line-height: 1.4;">
                        <a href="${status.url}" target="_blank" style="text-decoration: none; color: inherit;">
                            ${content}
                        </a>
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(err => {
            container.innerHTML = "Currently quiet in the tavern.";
            console.error(err);
        });
});
