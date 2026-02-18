document.getElementById("predictBtn").addEventListener("click", async () => {

    const payload = {
        income: document.getElementById("income").value,
        credit: document.getElementById("credit").value,
        annuity: document.getElementById("annuity").value,
        children: document.getElementById("children").value,
        bureau_year: document.getElementById("bureau_year").value,
        gender: document.getElementById("gender").value,
        car: document.getElementById("car").value,
        realty: document.getElementById("realty").value
    };

    const res = await fetch("/predict", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    });

    const data = await res.json();

    if(data.error){
        alert(data.error);
        return;
    }

    // Animate score counter
    let scoreElement = document.getElementById("cibil");
    let start = 300;
    let end = data.cibil_score;
    let increment = Math.ceil((end - start) / 50);

    let interval = setInterval(()=>{
        start += increment;
        if(start >= end){
            start = end;
            clearInterval(interval);
        }
        scoreElement.textContent = start;
    },20);

    // Update gauge
    let gauge = document.getElementById("gaugeFill");
    let percent = (data.cibil_score - 300) / 600;
    let offset = 502 - (502 * percent);
    gauge.style.strokeDashoffset = offset;

    // PD
    document.getElementById("pd").textContent = data.pd;

    // Risk badge
    let badge = document.getElementById("band");
    badge.textContent = data.risk_band;

    if(data.cibil_score < 550){
        badge.style.background="#ff4d4d";
    } else if(data.cibil_score < 650){
        badge.style.background="#ffa500";
    } else if(data.cibil_score < 750){
        badge.style.background="#4caf50";
    } else {
        badge.style.background="#00ff99";
    }

});
