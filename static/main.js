var timer,warningLevel=0,errorLevel=0;
ws = new WebSocket("ws://"+window.location.host+"/ws");

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

function objName(obj)
{
    return obj.company+":"+obj.ship+":"+obj.controller+":"+obj.instance;
}

function doError(obj)
{
    if(errorLevel>0)return;
    errorLevel=1;
    document.body.style.backgroundColor="red";
    alert("Error state for "+objName(obj));
}
function doWarning(obj)
{
    if(warningLevel<2) {warningLevel++;
    document.body.style.backgroundColor="yellow";
    alert("Warning state for "+objName(obj)+" level "+warningLevel)
    }
    else doError(obj)
}

ws.onmessage = function(evt) {
    var obj;
    eval("obj="+evt.data)
    if (obj.type === "error") doError(obj);
    else {
        if (timer !== null && typeof timer !== "undefined" && typeof timer[obj.company] !== "undefined" && typeof timer[obj.company][obj.ship] !== "undefined" && typeof timer[obj.company][obj.ship][obj.controller] !== "undefined" && typeof timer[obj.company][obj.ship][obj.controller][obj.instance] !== "undefined") clearInterval(timer[obj.company][obj.ship][obj.controller][obj.instance]);
        else if(timer==null)timer={};
        if(typeof timer[obj.company] === "undefined")timer[obj.company]={};
        if(typeof timer[obj.company][obj.ship] === "undefined")timer[obj.company][obj.ship]={};
        if(typeof timer[obj.company][obj.ship][obj.controller] === "undefined")timer[obj.company][obj.ship][obj.controller]={};
        if(typeof timer[obj.company][obj.ship][obj.controller][obj.instance] === "undefined")timer[obj.company][obj.ship][obj.controller][obj.instance]={};

        if(warningLevel>0)warningLevel--;
        if(errorLevel==0&&warningLevel==0) document.body.style.backgroundColor="green";
timer[obj.company][obj.ship][obj.controller][obj.instance] = setInterval(function() {
            doWarning(obj);
        }, 11000);
    }
}
