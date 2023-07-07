var textareaCount = 0;

function toggleFollowup() {
    var followupContainer = document.getElementById("followupContainer");
    var newFollowupTextarea = document.createElement("textarea");
    var removeButton = document.createElement("button");
    var addButton = document.getElementById("addButton");

    textareaCount++;
    newFollowupTextarea.name = "followupTextarea" + textareaCount;
    newFollowupTextarea.cols = "100";
    newFollowupTextarea.rows = "20";
    removeButton.textContent = "Remove";
    removeButton.onclick = function () {
        followupContainer.removeChild(newFollowupTextarea);
        followupContainer.removeChild(removeButton);
    };

    followupContainer.appendChild(newFollowupTextarea);
    followupContainer.appendChild(removeButton);
    followupContainer.appendChild(addButton);
}
function downloadCSV() {
    var csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Name,Email,Company\n";

    var encodedURI = encodeURI(csvContent);
    var link = document.createElement("a");
    link.setAttribute("href", encodedURI);
    link.setAttribute("download", "example.csv");
    document.body.appendChild(link); // Required for Firefox
    link.click();
}