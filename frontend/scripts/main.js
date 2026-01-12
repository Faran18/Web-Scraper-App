// API Base URL
const API_BASE = "http://localhost:8000/api";

// ==================== SCRAPE FORM ====================
const scrapeForm = document.getElementById("scrape-form");
if (scrapeForm) {
    scrapeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const url = document.getElementById("url").value;
        const css_selector = document.getElementById("css_selector").value || null;
        const xpath = document.getElementById("xpath").value || null;
        
        const resultDiv = document.getElementById("scrape-result");
        const errorDiv = document.getElementById("scrape-error");
        const submitBtn = scrapeForm.querySelector("button[type='submit']");
        
        // Hide previous results
        resultDiv.style.display = "none";
        errorDiv.style.display = "none";
        
        // Disable button
        submitBtn.disabled = true;
        submitBtn.textContent = "Scraping...";
        
        try {
            const response = await fetch(`${API_BASE}/scrape`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ url, css_selector, xpath })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success
                const message = `
                    <strong>URL:</strong> ${data.vector_db_result.url}<br>
                    <strong>Chunks stored:</strong> ${data.vector_db_result.chunks}<br>
                    <strong>Characters:</strong> ${data.vector_db_result.chars}<br>
                    <strong>Preview:</strong> ${data.vector_db_result.preview}
                `;
                document.getElementById("scrape-message").innerHTML = message;
                resultDiv.style.display = "block";
            } else {
                throw new Error(data.detail || "Scraping failed");
            }
        } catch (error) {
            // Show error
            document.getElementById("scrape-error-message").textContent = error.message;
            errorDiv.style.display = "block";
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = "Scrape Website";
        }
    });
}

// ==================== PROCESS FORM ====================
const processForm = document.getElementById("process-form");
if (processForm) {
    processForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const query = document.getElementById("query").value;
        const description = document.getElementById("description").value;
        
        const resultDiv = document.getElementById("process-result");
        const errorDiv = document.getElementById("process-error");
        const submitBtn = processForm.querySelector("button[type='submit']");
        
        // Hide previous results
        resultDiv.style.display = "none";
        errorDiv.style.display = "none";
        
        // Disable button
        submitBtn.disabled = true;
        submitBtn.textContent = "Processing...";
        
        try {
            const response = await fetch(`${API_BASE}/process`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ query, description })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Display LLM results
                const llmOutput = document.getElementById("llm-output");
                
                if (data.llm_result.error) {
                    // Handle errors in LLM response
                    llmOutput.innerHTML = `
                        <p><strong>Error:</strong> ${data.llm_result.error}</p>
                        <pre>${data.llm_result.raw_text || JSON.stringify(data.llm_result, null, 2)}</pre>
                    `;
                } else if (data.llm_result.result && Array.isArray(data.llm_result.result)) {
                    // Display formatted results
                    const resultsList = data.llm_result.result
                        .map(item => `<li>${item}</li>`)
                        .join("");
                    llmOutput.innerHTML = `<ul>${resultsList}</ul>`;
                } else {
                    llmOutput.innerHTML = `<pre>${JSON.stringify(data.llm_result, null, 2)}</pre>`;
                }
                
                // Show source URL
                if (data.source_url) {
                    const sourceLink = document.getElementById("source-link");
                    sourceLink.href = data.source_url;
                    sourceLink.textContent = data.source_url;
                } else {
                    document.querySelector(".source-url").style.display = "none";
                }
                
                resultDiv.style.display = "block";
            } else {
                throw new Error(data.detail || "Processing failed");
            }
        } catch (error) {
            // Show error
            document.getElementById("process-error-message").textContent = error.message;
            errorDiv.style.display = "block";
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = "Process with AI";
        }
    });
}

// ==================== SUBSCRIBE FORM ====================
const subscribeForm = document.getElementById("subscribe-form");
if (subscribeForm) {
    subscribeForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const email = document.getElementById("email").value;
        const site = document.getElementById("site").value;
        const css_selector = document.getElementById("sub_css_selector")?.value || "";
        const xpath = document.getElementById("sub_xpath")?.value || "";
        
        const resultDiv = document.getElementById("subscribe-result");
        const errorDiv = document.getElementById("subscribe-error");
        const submitBtn = subscribeForm.querySelector("button[type='submit']");
        
        // Hide previous results
        resultDiv.style.display = "none";
        errorDiv.style.display = "none";
        
        // Disable button
        submitBtn.disabled = true;
        submitBtn.textContent = "Subscribing...";
        
        try {
            // Create FormData for form submission
            const formData = new FormData();
            formData.append("email", email);
            formData.append("site", site);
            if (css_selector) formData.append("css_selector", css_selector);
            if (xpath) formData.append("xpath", xpath);
            
            const response = await fetch(`${API_BASE}/subscribe`, {
                method: "POST",
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Show success
                document.getElementById("subscribe-message").textContent = data.message;
                resultDiv.style.display = "block";
                
                // Reset form
                subscribeForm.reset();
            } else {
                throw new Error(data.detail || "Subscription failed");
            }
        } catch (error) {
            // Show error
            document.getElementById("subscribe-error-message").textContent = error.message;
            errorDiv.style.display = "block";
        } finally {
            // Re-enable button
            submitBtn.disabled = false;
            submitBtn.textContent = "Subscribe";
        }
    });
}