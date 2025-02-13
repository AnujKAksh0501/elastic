'use strict';

(function () {
    console.log("Custom Tag Manager Loaded");

    // Extract the unique_code from the script tag's `data-key` attribute
    const scriptTag = document.currentScript;
    const uniqueCode = scriptTag.getAttribute("data-key");

    if (!uniqueCode) {
        console.error("No unique_code provided! Tracking will not work.");
        return;
    }

    console.log("Using Unique Code:", uniqueCode);

    // Function to dynamically load a script
    function loadScript(url, callback) {
        let script = document.createElement("script");
        script.type = "text/javascript";
        script.src = `${url}?unique_code=${uniqueCode}`;
        script.async = true;

        script.onload = function () {
            console.log("Loaded:", url);
            if (callback) callback();
        };

        script.onerror = function () {
            console.error("Failed to load:", url);
        };

        document.head.appendChild(script);
    }

    // URLs of the scripts to load dynamically
    const scripts = [
        "https://mailer.apptexit.com/track.js",
    ];

    // Load each script
    scripts.forEach(url => loadScript(url));
})();