loadXMLDoc()
setInterval(loadXMLDoc, 2000);

function loadXMLDoc() {
    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            parseXML(this);
        }
    };
    xhttp.open("GET", "table.xml", true);
    xhttp.send();
}

function parseXML(xml) {
    // Variable for loop
    var i;

    // Create parser
    var parser = new DOMParser();

    // XML file
    var xmlDoc = parser.parseFromString(xml.responseText, "application/xml");

    // Create table headers
    table =
        '<thead dir="rtl">' +
            '<tr>' +
                '<th></th>' +
                '<th> שחר </th>' +
                '<th> מחיר ביקוש </th>' +
                '<th> מחיר היצע </th>' +
            '</tr>' +
        '</thead>' +
        '<tbody dir="rtl">'
    ;

    // Update all the rows from the XML
    var rows = xmlDoc.getElementsByTagName("stats")[0].childNodes;
    for (i = 0; i < rows.length; i++) {
        table += '<tr>' + '<td class="center">' + (i+1) + '</td>';
        table += '<td>' + rows[i].nodeName.slice(1) + '</td>';

        if (rows[i].getElementsByTagName("sc")[0].childNodes[0].nodeValue == "t"){
            table += '<td class="colored">';
        } else {
            table += '<td>';
        }
        table += rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>';

        if (rows[i].getElementsByTagName("tc")[0].childNodes[0].nodeValue == "t"){
            table += '<td class="colored">';
        } else {
            table += '<td>';
        }
        table += rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>' + '</tr>';
    }
    table += '</tbody>'

    // Update the inner HTML
    document.getElementById("demo").innerHTML = table;
}
