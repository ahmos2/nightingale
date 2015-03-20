var state={};
ws = new WebSocket("ws://" + window.location.host + "/ws");

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

function setDivColor4Obj(obj,color)
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
    if(state[objName(obj)].warningLevel < 2)
    {
        state[objName(obj)].warningLevel++;
        setDivColor4Obj(obj, "yellow");
        alert("Warning state for " + objName(obj) + " level " + state[objName(obj)].warningLevel)
    }
    else doError(obj)
}

ws.onmessage = function(evt) {
    var obj;
    eval("obj=" + evt.data)
    if(state[objName(obj)] === null || state[objName(obj)] === undefined)
        state[objName(obj)]=
            {
                errorLevel : 0,
                warningLevel : 0,
                timer : 0
            };

    if (obj.type === "error") doError(obj);
    else {
        if(state[objName(obj)].timer! = 0) clearInterval(state[objName(obj)].timer);
        if(state[objName(obj)].warningLevel > 0)state[objName(obj)].warningLevel--;
        if(state[objName(obj)].errorLevel == 0&&state[objName(obj)].warningLevel == 0) setDivColor4Obj(obj,"green");
        state[objName(obj)].timer = setInterval(function() {
            doWarning(obj);
        }, 11000);
    }
}
