'use strict'

document.addEventListener("DOMContentLoaded", async function(){
    let startTime = Date.now(); // Track page load time

    // Function to get URL query parameters
    function getQueryParam(param) {
        let urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(param);
    }

    const uniqueCode = getQueryParam("unique_code") || "UNKNOWN";
    let visitorIP = null;
    let visitorId = null;
    let visitId = null;
    let leadID = null;

    // Function to calculate time spent
    function getTimeSpent() {
        let timeSpentMs = Date.now() - startTime;
        return Math.floor(timeSpentMs / 1000); // Convert milliseconds to seconds
    }

    // Function to get current date and time
    function getCurrentDateTime() {
        const now = new Date();
        return {
            date: now.toISOString().split("T")[0], // YYYY-MM-DD
            time: now.toTimeString().split(" ")[0] // HH:MM:SS
        };
    }

    // Function to detect browser
    function getBrowser() {
        const userAgent = navigator.userAgent;

        // Check for Firefox
        if (userAgent.indexOf("Firefox") > -1) {
            return "Firefox";
        }
        // Check for Chrome (must be after Firefox since Chrome also contains "Firefox" in its user agent)
        if (userAgent.indexOf("Chrome") > -1 && userAgent.indexOf("Safari") > -1) {
            return "Chrome";
        }
        // Check for Safari (must be after Chrome since Safari also contains "Chrome" in its user agent)
        if (userAgent.indexOf("Safari") > -1 && userAgent.indexOf("Chrome") === -1) {
            return "Safari";
        }
        // Check for Microsoft Edge
        if (userAgent.indexOf("Edg") > -1) {
            return "Microsoft Edge";
        }
        // Check for Internet Explorer
        if (userAgent.indexOf("Trident") > -1 || userAgent.indexOf("MSIE") > -1) {
            return "Internet Explorer";
        }
        // Check for Opera
        if (userAgent.indexOf("Opera") > -1 || userAgent.indexOf("OPR") > -1) {
            return "Opera";
        }
        // Check for Brave
        if (userAgent.indexOf("Brave") > -1) {
            return "Brave";
        }
        // Check for Tor
        if (userAgent.indexOf("Tor") > -1) {
            return "Tor";
        }

        // If none of the above, return "Unknown"
        return "Unknown";
    }

    // Function to detect OS details
    function getOsDetails(){
        const ua = navigator.userAgent;
        let os = "Unknown OS";
        let osVersion = "Unknown OS Version";

        // Detect Windows OS and Version
        if (/Windows NT 10.0/i.test(ua)) {
            os = "Windows";
            if (/Win64|x64|WOW64/i.test(ua)) {
                osVersion = "Windows 11"; // Assuming Win64 on Windows 10 is Windows 11
            } else {
                osVersion = "Windows 10";
            }
        } else if (/Windows NT 6.3/i.test(ua)) {
            os = "Windows";
            osVersion = "Windows 8.1";
        } else if (/Windows NT 6.2/i.test(ua)) {
            os = "Windows";
            osVersion = "Windows 8";
        } else if (/Windows NT 6.1/i.test(ua)) {
            os = "Windows";
            osVersion = "Windows 7";
        } else if (/Android/i.test(ua)) {
            os = "Android";
            let match = ua.match(/Android (\d+(\.\d+)?)/i);
            osVersion = match ? `Android ${match[1]}` : "Unknown Android Version";
        } else if (/iPhone|iPad|iPod/i.test(ua)) {
            os = "iOS";
            let match = ua.match(/OS (\d+_\d+)/i);
            osVersion = match ? `iOS ${match[1].replace('_', '.')}` : "Unknown iOS Version";
        } else if (/Mac OS X/i.test(ua)) {
            os = "macOS";
            let match = ua.match(/Mac OS X (\d+_\d+(_\d+)?)/i);
            osVersion = match ? `macOS ${match[1].replace(/_/g, '.')}` : "Unknown macOS Version";
        } else if (/Linux/i.test(ua)) {
            os = "Linux";
            osVersion = "Unknown Linux Version";
        }

        return { os, osVersion };
    }

    // Function to detect device, model & brand (limited accuracy)
    function getDeviceDetails() {
        const ua = navigator.userAgent;
        let device = 'Others';
        let brand = "Other Brand";
        let model = "Unknown Model";

        // Detect Mobile, Tablet, Laptop, Desktop, Wearable
        if (/Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(ua)) {
            device = "Mobile";
        } else if (/Tablet|iPad/i.test(ua)) {
            device = "Tablet";
        } else if (/Mac|Windows NT|Linux/i.test(ua) && !/Mobi/i.test(ua)) {
            device = "Desktop/Laptop";
        } else if (/Watch|Wearable/i.test(ua)) {
            device = "Wearable";
        }

        // Detect Apple Devices (iPhone, iPad, Mac)
        if (/iPhone/i.test(ua)) {
            brand = "Apple";
            let match = ua.match(/iPhone\s(\d+)/);
            model = match ? `iPhone ${match[1]}` : "iPhone";
        } else if (/iPad/i.test(ua)) {
            brand = "Apple";
            model = "iPad";
        } else if (/Mac/i.test(ua)) {
            brand = "Apple";
            model = "MacBook";
        } else if (/SM-|GT-|SCH-|Galaxy/i.test(ua)) {
            brand = "Samsung";
            let match = ua.match(/SM-(\w+)|GT-(\w+)|SCH-(\w+)|Galaxy (\w+)/);
            model = match ? match[0].replace(/_/g, " ") : "Samsung Device";
        } else if (/OnePlus/i.test(ua)) {
            brand = "OnePlus";
            let match = ua.match(/OnePlus (\w+)/);
            model = match ? `OnePlus ${match[1]}` : "OnePlus Device";
        } else if (/Pixel/i.test(ua)) {
            brand = "Google";
            let match = ua.match(/Pixel (\w+)/);
            model = match ? `Pixel ${match[1]}` : "Pixel Device";
        } else if (/Redmi|Mi|POCO/i.test(ua)) {
            brand = "Xiaomi";
            let match = ua.match(/(Redmi|Mi|POCO) (\w+)/);
            model = match ? match[0] : "Xiaomi Device";
        } else if (/Oppo/i.test(ua)) {
            brand = "Oppo";
            let match = ua.match(/Oppo (\w+)/);
            model = match ? `Oppo ${match[1]}` : "Oppo Device";
        } else if (/Vivo/i.test(ua)) {
            brand = "Vivo";
            let match = ua.match(/Vivo (\w+)/);
            model = match ? `Vivo ${match[1]}` : "Vivo Device";
        } else if (/Realme/i.test(ua)) {
            brand = "Realme";
            let match = ua.match(/Realme (\w+)/);
            model = match ? `Realme ${match[1]}` : "Realme Device";
        } else if (/Nokia/i.test(ua)) {
            brand = "Nokia";
            let match = ua.match(/Nokia (\w+)/);
            model = match ? `Nokia ${match[1]}` : "Nokia Device";
        } else if (/Sony/i.test(ua)) {
            brand = "Sony";
            let match = ua.match(/Sony (\w+)/);
            model = match ? `Sony ${match[1]}` : "Sony Device";
        } else if (/Moto|Motorola/i.test(ua)) {
            brand = "Motorola";
            let match = ua.match(/Moto (\w+)|Motorola (\w+)/);
            model = match ? match[0] : "Motorola Device";
        } else if (/BlackBerry/i.test(ua)) {
            brand = "BlackBerry";
            model = "BlackBerry Device";
        } else if (/Nothing/i.test(ua)) {
            brand = "Nothing";
            let match = ua.match(/Nothing (\w+)/);
            model = match ? `Nothing ${match[1]}` : "Nothing Device";
        } else if (/Lava/i.test(ua)) {
            brand = "Lava";
            let match = ua.match(/Lava (\w+)/);
            model = match ? `Lava ${match[1]}` : "Lava Device";
        } else if (/Micromax/i.test(ua)) {
            brand = "Micromax";
            let match = ua.match(/Micromax (\w+)/);
            model = match ? `Micromax ${match[1]}` : "Micromax Device";
        } else if (/Asus/i.test(ua)) {
            brand = "Asus";
            let match = ua.match(/Asus (\w+)/);
            model = match ? `Asus ${match[1]}` : "Asus Device";
        } else if (/Huawei|Honor/i.test(ua)) {
            brand = "Huawei";
            let match = ua.match(/(Huawei|Honor) (\w+)/);
            model = match ? match[0] : "Huawei Device";
        } else if (/Android/i.test(ua)) {
            brand = "Android";
            let match = ua.match(/\(([^)]+)\)/);
            if (match) {
                let details = match[1].split(";");
                if (details.length > 2) {
                    model = details[2].trim();
                    brand = details[1].trim();
                } else {
                    model = "Android Device";
                }
            }
        }

        return { device, model, brand };
    }

    try{
        let ipResponse = await fetch("https://api.ipify.org/?format=json");
        let ipData = await ipResponse.json();
        visitorIP = ipData.ip;
        console.log("User IP:", ipData.ip);

        const osDetails = getOsDetails();
        const deviceDetails = getDeviceDetails();

        const visitorDetails = {
            uniqueCode: uniqueCode,
            source: window.location.hostname,
            ipAddress: visitorIP,
            userAgent: navigator.userAgent,
            platform: osDetails.os,
            platformVersion: osDetails.osVersion,
            browser: getBrowser(),
            language: navigator.language,
            screenResolution: `${window.screen.width}x${window.screen.height}`,
            device: deviceDetails.device,
            deviceModel: deviceDetails.model,
            deviceBrand: deviceDetails.brand
        };

        let visitorResponse = await fetch("https://mailerapi2.apptexit.com/api/v1/visitor-capture", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(visitorDetails)
        });

        console.log("Visitor Capture Response:", await visitorResponse.json());

        let visitorResult = await visitorResponse.json();

        // Ensure visitor details were successfully captured before sending visiting details
        if (visitorResponse.ok && visitorResult.success) {
            visitorId = visitorResult.visitorId; // Get visitor ID from response
            console.log("Captured Visitor ID:", visitorId);

            /// Capture time spent when user leaves or closes the page
            async function sendVisitDetails() {
                let timeSpent = getTimeSpent(); // Get time spent on the page
                console.log("Time Spent on Page:", timeSpent, "seconds");

                const visitingDetails = {
                    uniqueCode: uniqueCode,
                    visitorId: visitorId,  // Send visitorId to visit capture API
                    ipAddress: visitorIP,
                    pageVisited: window.location.href,
                    referrer: document.referrer || "Direct",
                    visitTimestamp: new Date().toISOString(),
                    timeSpent: timeSpent // Send time spent
                };

                // Second API Call: Capture Visiting Details
                let visitResponse = await fetch("https://mailerapi2.apptexit.com/api/v1/visit-capture", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(visitingDetails)
                })
                
                let visitResult = await visitResponse.json();

                if(visitResponse.ok && visitResult.success){
                    visitId = visitResult.visitId;
                    console.log("Captured Visit ID:", visitId);
                }else{
                    console.warn("Visitor details not captured successfully.");
                }
            }

            await sendVisitDetails();

            // Capture time spent when user leaves the page
            window.addEventListener("beforeunload", sendVisitDetails);
        } else {
            console.warn("Visitor details were not captured successfully. Skipping visit capture.");
        }
    }catch (error) {
        console.error("Error:", error);
    }

    const form = document.querySelector(".quote-form"); // Select the form
    const apiFormCaptureUrl = "https://mailerapi2.apptexit.com/api/v1/form-data-capture"; // API endpoint
    const apiSendEmailUrl = "https://mailerapi2.apptexit.com/api/v1/form-data-send-mail"; // API to send email immediately
    const thankYouPage = "https://mailer.apptexit.com/thank-you"; // Thank you page URL

    let formData = {}; // Store form data
    let timeout = null; // Timer to delay API calls

    // Function to collect form data
    function collectFormData() {
        const { date, time } = getCurrentDateTime();

        formData = {
            visitorIP: visitorIP || "",
            visitorID: visitorId || "",
            visitID: visitId || "",
            uniqueCode: uniqueCode,
            source: window.location.hostname,
            part: document.querySelector("#part")?.value || "",
            make: document.querySelector("#make")?.value || "",
            model: document.querySelector("#model")?.value || "",
            year: document.querySelector("#year")?.value || "",
            size: document.querySelector("#size")?.value || "",
            name: document.querySelector("#name")?.value || "",
            phone: document.querySelector("#phone")?.value || "",
            email: document.querySelector("#email")?.value || "",
            isPremium: "No",
            date: date,
            time: time
        };
        console.log("Form Data Captured:", formData);
    }

    // Function to handle user input
    function handleInput() {
        let formData = collectFormData(); // Update form data

        clearTimeout(timeout); // Reset timer
        timeout = setTimeout(async () => {
            try {
                if (Object.values(formData).some(value => value.trim() !== "")) { // Ensure at least one field has data
                    let captureResponse = await fetch(apiFormCaptureUrl, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(formData)
                    });
    
                    let captureResult = await captureResponse.json();

                    if (captureResponse.ok && captureResult.success) {
                        leadID = captureResult.lead;
                    }
                }
            } catch (error) {
                console.error("Error saving form data:", error);
                return null;
            }
        }, 3000); // Wait 3 seconds after user input
    }

    // Attach input event listeners to form fields
    document.querySelectorAll("#captureForm input, #captureForm select, #captureForm textarea").forEach(field => {
        field.addEventListener("input", handleInput); // Capture user input
    });

    // Handle form submission (redirect to thank-you page)
    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission
        try {
            let formData = collectFormData(); // Update form data

            if (Object.values(formData).some(value => value.trim() !== "")) { // Ensure at least one field has data
                let captureResponse = await fetch(apiFormCaptureUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(formData)
                });

                let captureResult = await captureResponse.json();
                
                if (captureResponse.ok && captureResult.success) {
                    leadID = captureResult.lead;
                }
            }
        } catch (error) {
            console.error("Error saving form data:", error);
            return null;
        }
        window.location.href = thankYouPage; // Redirect to thank-you page
    });

    // Function to send email immediately and delete the queue
    async function sendEmailNow(uniqueCode, leadID, isPremium) {
        try {
            leadData = {
                uniqueCode: uniqueCode,
                leadID: leadID,
                isPremium: isPremium,
            }

            let mailResponse = await fetch(apiSendEmailUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(leadData)
            });

            let mailResult = await mailResponse.json();

            if (mailResponse.ok && mailResult.success) {
                console.log("Email Status:", response.status);
            }
        } catch (error) {
            console.error("Error saving form data:", error);
            return null;
        }
    }

    const callButton = document.querySelector(".call-btn"); // Select call button
    if (callButton){
        // Handle call button click (send email immediately & delete queue)
        callButton.addEventListener("click", async function () {
            await sendEmailNow(uniqueCode, leadID, 'Yes');
        });
    }

    // Send email if user is inactive for 60 seconds
    setTimeout(async function () {
        await sendEmailNow(uniqueCode, leadID, 'No');
    }, 60000);

    // Send data when the user leaves the page
    window.addEventListener("beforeunload", async function () {
        await sendEmailNow(uniqueCode, leadID, 'No');
    });
});