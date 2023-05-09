var websocket = new WebSocket('ws://localhost:8000/ws/');

var audioContext = new AudioContext();

var log = document.getElementById("log");

var handleSuccess = function(stream) {
    var context = new AudioContext();
    var source = context.createMediaStreamSource(stream);
    var processor = context.createScriptProcessor(1024, 1, 1);
    var chat_message_tag = document.querySelector("#chat_messages");
    var flag = false;
    var first = true;

    var recording = false;

    source.connect(processor);
    processor.connect(context.destination);

    var buffer = [];

    recordEventListner = function() {
        if (recording == false){
            document.getElementById("recordButton").classList.add("recording");
            change_default_message(1);
        } else{
            document.getElementById("recordButton").classList.remove("recording");
            websocket.close();
            create_result_button();
        }
        recording = !recording;
    }

    document.getElementById("recordButton").addEventListener("click", recordEventListner);

    close_websocket = function(){
        document.getElementById("recordButton").classList.remove("recording");
        websocket.close();
        recording = !recording;
    }

    create_result_button = function(){
        const recordButton = document.getElementById("recordButton");
        const outerCircle = document.querySelector(".outer-circle");
        const innerCircle = document.querySelector(".inner-circle");

        if (outerCircle && innerCircle) {
            outerCircle.remove();
            innerCircle.remove();

            recordButton.style.borderRadius="0.5em";
            recordButton.style.width = "10em";
            recordButton.style.height = "2em";
            recordButton.style.fontSize = "1.5em";
            recordButton.style.color = "white";
            recordButton.style.fontWeight = "bold";
            recordButton.innerHTML = "Go To Result";
        }

        change_default_message(2);
        recordButton.removeEventListener("click", recordEventListner);
        recordButton.addEventListener("click", change_button_click_event);
    }

    change_default_message = function(flag){
        const default_message = document.querySelector("#default-message");
        if (flag == 1){
            default_message.innerHTML = "녹음을 중지하려면, 아래의 버튼을 눌러주세요";
        }

        if (flag == 2){
            default_message.innerHTML = "결과를 확인하려면, 아래의 버튼을 눌러주세요";
        }
    }

    change_button_click_event = function(){
        window.location.href = "/result";
    }

    processor.onaudioprocess = function(e) {
        if (!recording) return;
        buffer.push(new Float32Array(e.inputBuffer.getChannelData(0)));
        
    };

    websocket.onmessage = function(event){
        const msg = JSON.parse(event.data);

        if ("res1" in msg){
            res1 = msg["res1"]
            res2 = msg["res2"]

            const parentElement = chat_message_tag;
            const children = parentElement.querySelectorAll(':scope > *');
            const secondChildFromBehind = children[children.length - 2];
            const thirdChildFromBehind = children[children.length - 3]; 
            
            if (typeof secondChildFromBehind !== 'undefiend'){
                if (msg["res1"] == "1"){
                    secondChildFromBehind.firstChild.className = "abuse-sentence";
                } else if (msg["res1"] == "2"){
                    secondChildFromBehind.firstChild.className = "sexual-sentence";
                }
            }
            if (typeof thirdChildFromBehind !== 'undefined'){
                if (msg["res2"] == "1"){
                    thirdChildFromBehind.firstChild.className = "abuse-sentence";
                } else if (msg["res2"] == "2"){
                    thirdChildFromBehind.firstChild.className = "sexual-sentence";
                }
            }

        }
        else{

            if (flag == false && first == true){
                first = false;
                const element = document.createElement("div");
                element.className = "chat-message";

                const wrapper = document.createElement("div");
                wrapper.textContent = msg['text'];

                element.appendChild(wrapper);

                chat_message_tag.appendChild(element);
                chat_message_tag.scrollTop = chat_message_tag.scrollHeight;

                var cName = "normal-sentence";
                res = msg['res'];
                if (res == "1") {cName = "abuse-sentence";}
                if (res == "2") {cName = "sexual-sentence";}
                chat_message_tag.lastChild.lastChild.className = cName;
            }
            else if (flag == false){
                chat_message_tag.lastChild.lastChild.innerHTML = msg['text'];
                var cName = "normal-sentence";
                res = msg['res'];
                if (res == "1") {cName = "abuse-sentence";}
                if (res == "2") {cName = "sexual-sentence";}
                chat_message_tag.lastChild.lastChild.className = cName;

                chat_message_tag.scrollTop = chat_message_tag.scrollHeight;

            }
            else{
                flag = false;
                const element = document.createElement("div");
                element.className = "chat-message";

                const wrapper = document.createElement("div");
                wrapper.textContent = msg['text'];
                element.appendChild(wrapper);

                chat_message_tag.appendChild(element);
                chat_message_tag.scrollTop = chat_message_tag.scrollHeight;
            }
            flag = (msg['final'] === "true");

            if ("time" in msg){
                const element = chat_message_tag.lastChild;
                const wrapper = document.createElement("span");
                wrapper.className = "chat-time";
                wrapper.textContent = msg['time'];
                element.appendChild(wrapper);
            }

            if (msg["stop_flag"] == "True"){
                const default_message = document.querySelector("#default-message");
                const default_start_message = document.querySelector("#default-start-message");
                const abuse_cnt_message = document.querySelector("#abuse-cnt-message");
                const default_middle_message = document.querySelector("#default-middle-message");
                const sexual_cnt_message = document.querySelector("#sexual-cnt-message");
                const default_last_message = document.querySelector("#default-last-message");
                
                default_start_message.innerHTML = "해당 사용자는 ";
                abuse_cnt_message.innerHTML = "(폭언 : " + msg["abuse_cnt"] + "회";
                default_middle_message.innerHTML = " | ";
                sexual_cnt_message.innerHTML = "성희롱 : " + msg["sexual_cnt"] + "회)";
                default_last_message.innerHTML = "에 해당하므로 자동으로 강제 종료됩니다";                    
                
                close_websocket();
                create_result_button();
                default_message.innerHTML = "";

            }
        }
        
    }

    setInterval(function() {
        if (buffer.length === 0) return;
        var data = buffer.splice(0, buffer.length);
        var outputBuffer = new Int16Array(data.length * data[0].length);
        for (let i = 0, index = 0; i < data.length; i++) {
        for (let k = 0; k < data[i].length; k++, index++){
            outputBuffer[index] = data[i][k] * 32767;
        }
        }
        websocket.send(outputBuffer)
    }, 1000);
};

navigator.mediaDevices.getUserMedia({ audio: true, video: false })
    .then(handleSuccess);