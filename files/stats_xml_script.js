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
        '<thead>' +
            '<tr>' +
                '<th></th>' +
                '<th> hello </th>' +
                '<th> מחיר ביקוש </th>' +
                '<th> מחיר היצע </th>' +
            '</tr>' +
        '</thead>' +
        '<tbody>'
    ;

    // Update all the rows from the XML
    var rows = xmlDoc.getElementsByTagName("stats")[0].childNodes;
    for (i = 0; i < rows.length; i++) {
        table += '<tr>' + '<td class="center">' + (i+1) + '</td>';
        table += '<td class="colored_cell">' + rows[i].nodeName.slice(1) + '</td>';

        switch (rows[i].nodeName.slice(0, 1)) {
            case "b":
                table += '<td class="colored">' + rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>';
                table += '<td>' + rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>';
                break;
            case "c":
                table += '<td>' + rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>';
                table += '<td class="colored">' + rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>';
                break;
            case "d":
                table += '<td class="colored">' + rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>';
                table += '<td class="colored">' + rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>';
                break;
            default:
                table += '<td>' + rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>';
                table += '<td>' + rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>';
        }
        table += '</tr>';

    }
    table += '</tbody>'

    // Update the inner HTML
    document.getElementById("demo").innerHTML = table;
}
