var AliveTooSoonAction = 2, AliveTooLateAction = 1;
var WarningEscalate2ErrorTrigger = 2;
var slack = 500;
var timeoutCheckTime = 1000;

var state={};
var ws = new WebSocket("wss://" + window.location.host + "/ws");

function ms2time(ms) {
    var time = ms / 3600000;
    var hour = Math.floor(time);
    time -= Math.floor(time);
    time *= 60;
    var minute = Math.floor(time);
    time -= Math.floor(time);
    time *= 60;
    var second = Math.floor(time);
    return {
        "h": hour,
        "m": minute,
        "s": second
    };
}

function setDivColor4Obj(obj, color)
{
    var div = document.getElementById(objName(obj));
    if(div === null) 
    {
        div = document.createElement('div');
        div.id = objName(obj);
        div.style.height = "100px";
        div.style.width = "100px";
        div.innerText = objName(obj);
        document.getElementsByTagName('body')[0].appendChild(div);
    }
    div.style.backgroundColor = color;
}

function objName(obj)
{
    return obj.company + ":" + obj.ship + ":" + obj.controller + ":" + obj.instance;
}

function doError(obj)
{
    if(state[objName(obj)].errorLevel > 0) return;
    state[objName(obj)].errorLevel = 1;
    setDivColor4Obj(obj, "red");
    alert("Error state for " + objName(obj));
}
function doWarning(obj)
{
    if(WarningEscalate2ErrorTrigger <= 0 || state[objName(obj)].warningLevel < WarningEscalate2ErrorTrigger)
    {
        state[objName(obj)].warningLevel++;
        setDivColor4Obj(obj, "yellow");
        alert("Warning state for " + objName(obj) + " level " + state[objName(obj)].warningLevel)
    }
    else doError(obj)
}

var xhr=new XMLHttpRequest()
xhr.onload=function(e) {
    var o=JSON.parse(xhr.responseText)
    state=o;

    for(var instanceName in state) {
        state[instanceName].timer=state[instanceName].lastMessageTs=0;
        if(state[instanceName].lastError!=undefined) {state[instanceName].errorLevel=0;doError(state[instanceName]);}
        else setDivColor4Obj(state[instanceName], "green");
    }
}
xhr.open("GET", "/State", true);
xhr.send();

ws.onerror = function(evt) {console.log("WebSocket error");alert("WebSocket error");document.getElementById("wsStateDiv").style.backgroundColor="yellow";}
ws.onclose = function(evt) {console.log("WebSocket disconnect");alert("WebSocket disconnect");document.getElementById("wsStateDiv").style.backgroundColor="red";}
ws.onopen = function(evt) {console.log("WebSocket connect");document.getElementById("wsStateDiv").style.backgroundColor="green";}
ws.onmessage = function(evt) {
    document.getElementById("wsStateDiv").style.backgroundColor="green";
    var obj=JSON.parse(evt.data);
    if(state[objName(obj)] === null || state[objName(obj)] === undefined)
        state[objName(obj)]=
            {
                errorLevel : 0,
                warningLevel : 0,
                timer : 0,
                lastMessageTs : 0
            };

    var nowTs=new Date().getTime();

    if (obj.type === "error") doError(obj);
    else if(obj.type === "alive") {
        if(state[objName(obj)].timer != 0) clearInterval(state[objName(obj)].timer);
        if(state[objName(obj)].warningLevel > 0)state[objName(obj)].warningLevel--;

        if(state[objName(obj)].lastMessageTs != 0) {
            usedSlack = nowTs - state[objName(obj)].lastMessageTs - 10000;
            console.log(nowTs+","+state[objName(obj)].lastMessageTs)
            if(usedSlack  < -slack) {
                console.log("Got message too soon");
                if(AliveTooSoonAction === 1) doWarning(obj);
                else if(AliveTooSoonAction === 2) doError(obj);
            }
            if(state[objName(obj)].lastMessageTs != 0) console.log("used slack " + usedSlack);
        }
        state[objName(obj)].lastMessageTs = nowTs;

        if(state[objName(obj)].errorLevel == 0 && state[objName(obj)].warningLevel == 0) setDivColor4Obj(obj, "green");
        state[objName(obj)].timer = setInterval(function() {
            if(new Date().getTime() > nowTs + 10000 + slack) {
                console.log("Timeout for "+objName(obj));
                if(AliveTooLateAction === 1)
                    doWarning(obj);
                if(AliveTooLateAction === 2) 
                    doError(obj);
            }
        }, timeoutCheckTime);
    }
}

function ResetErrorState() {
    for(var instanceName in state) {
        nameParts=instanceName.split(':');
        var xhr=new XMLHttpRequest();
        xhr.open("GET", "/ResetErrorState?company="+nameParts[0]+"&ship="+nameParts[1]+"&controller="+nameParts[2]+"&instance="+nameParts[3],false);
        xhr.send();
    }
    location.reload();
}
