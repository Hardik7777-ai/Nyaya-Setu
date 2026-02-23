document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const ui = {
        btn: document.getElementById('analyzeBtn'),
        input: document.getElementById('legalInput'),
        lang: document.getElementById('langSelect'),
        output: document.getElementById('outputResult'),
        loader: document.getElementById('loadingIndicator')
    };

    const handleInference = async () => {
        const textPayload = ui.input.value.trim();
        
        if (textPayload.length < 15) {
            alert("Please provide a valid legal document (min 15 characters).");
            return;
        }

        // State management: loading
        ui.btn.disabled = true;
        ui.btn.innerText = "Processing...";
        ui.loader.classList.remove('hidden');
        ui.output.innerText = "";

        try {
            const res = await fetch("http://localhost:8000/api/v1/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    raw_text: textPayload, 
                    target_lang: ui.lang.value 
                })
            });

            if (!res.ok) throw new Error(`Server returned ${res.status}`);

            const jsonResponse = await res.json();
            
            // Format the output for readability
            if (jsonResponse.status === "success") {
                const parsedData = JSON.parse(jsonResponse.data);
                ui.output.innerText = JSON.stringify(parsedData, null, 2);
            }

        } catch (err) {
            console.error("Pipeline Error:", err);
            ui.output.innerText = "Connection failed. Please verify the API server is running.";
        } finally {
            // State management: reset
            ui.btn.disabled = false;
            ui.btn.innerText = "Run Analysis Pipeline";
            ui.loader.classList.add('hidden');
        }
    };

    ui.btn.addEventListener('click', handleInference);
});
