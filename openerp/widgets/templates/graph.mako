<div class="graph-block" style="text-align: center; padding: 10px; min-width: $width">

    <div id="${name}"></div>
    
    <script type="text/javascript">
        var get_chart_${name} = function(name){
            var res = ${data|n};
            return MochiKit.Base.serializeJSON(res);
        }
        
        swfobject.embedSWF(getURL("/static/open-flash-chart.swf"), "${name}", "${width}", "${height}", "9.0.0", 
        "expressInstall.swf", {'get-data': 'get_chart_${name}'}, {'wmode': 'transparent'});
    </script>
    
</div>

