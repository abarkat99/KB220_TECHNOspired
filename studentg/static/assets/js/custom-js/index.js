
function autocomplete() {
    var arr;
    arr = array_big;
    document.getElementById('myInput').addEventListener("input", function (e) {
        var a, b, i, val = this.value;
        if (!val) return false;
        const loc = document.getElementById('loc');
        if (val.length == 6) {
            for (i = 0; i < arr.length; i++)
                if (arr[i].toUpperCase().includes(val.toUpperCase())) b = "<i class='fa fa-map-marker' style='color: red'></i> " + arr[i].substr(9, arr[i].length);
            loc.innerHTML = b;
        } else b = "";
        loc.innerHTML = b;
    });
}

if (document.getElementById('myInput') != null) autocomplete();
