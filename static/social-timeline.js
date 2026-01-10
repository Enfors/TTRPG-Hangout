document.addEventListener("DOMContentLoaded", function() {
    const instance = "https://ttrpg-hangout.social";
    const container = document.getElementById("mastodon-timeline");
    
    // Fetch local timeline, limit to 5 posts
    fetch(`${instance}/api/v1/timelines/public?local=true&limit=5`)
        .then(response => response.json())
        .then(data => {
            container.innerHTML = "";
            
            data.forEach(status => {
                // 1. RESPECT PRIVACY
                if (status.account.noindex === true || status.account.discoverable === false) {
                    return; 
                }

                const div = document.createElement("div");
                div.className = "toot-entry";
                
                // Outer Spacing
                div.style.marginBottom = "10px"; 
                div.style.paddingBottom = "10px";
                div.style.borderBottom = "1px solid #eee";
                
                // Content Prep
                let content = status.content;
                if (status.spoiler_text) {
                    content = `<p style="margin:0;"><strong>CW: ${status.spoiler_text}</strong> <br> 
                               <span style="font-size:0.8rem; color:#666;">(Click to view)</span></p>`;
                } else {
                    content = content.replace(/<p>/g, '<p style="margin: 0; margin-bottom: 5px;">');
                }

                // IMAGE ATTACHMENTS
                let attachments = "";
                if (status.media_attachments && status.media_attachments.length > 0) {
                    status.media_attachments.forEach(att => {
                        if (att.type === "image") {
                            attachments += `
                                <div style="margin-top: 10px;">
                                    <a href="${att.url}" target="_blank">
                                        <img src="${att.preview_url}" 
                                             alt="${att.description || 'Image'}" 
                                             style="max-width: 500px; width: 100%; height: auto; border-radius: 8px; border: 1px solid #eee;">
                                    </a>
                                </div>
                            `;
                        }
                    });
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
                        ${attachments}
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
