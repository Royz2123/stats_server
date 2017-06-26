loadXMLDoc()
setInterval(loadXMLDoc, 1000);

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
                '<th> First Header </th>' +
                '<th> Second Header </th>' +
                '<th> Third Header </th>' +
            '</tr>' +
        '</thead>' +
        '<tbody>'
    ;
        
    // Update all the rows from the XML
    var rows = xmlDoc.getElementsByTagName("row"); 
    for (i = 0; i < rows.length; i++) {
        table += 
            '<tr>' +
                '<td class="center" rowspan="2">' + (i+1) + '</td>' +
                '<td>' + rows[i].getElementsByTagName("f")[0].childNodes[0].nodeValue + '</td>' + 
                '<td>' + rows[i].getElementsByTagName("s")[0].childNodes[0].nodeValue + '</td>' +
                '<td>' + rows[i].getElementsByTagName("t")[0].childNodes[0].nodeValue + '</td>' +
            '</tr>'
        ;
    }
    table += '</tbody>'
    
    // Update the inner HTML
    document.getElementById("demo").innerHTML = table;
}