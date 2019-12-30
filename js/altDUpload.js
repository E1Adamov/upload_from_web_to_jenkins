altDDumpFile.oninput = function() {

    const zipContent = this.files[0];
    getFilePaths(zipContent, function(filePaths)
    {
        acceptablePathsToLogfile = getAcceptablePathsToLogfile();

        let isValidAltD = false;

        for (const acceptablePathToLogfile of acceptablePathsToLogfile) {
            if (filePaths.includes(acceptablePathToLogfile)) {
                isValidAltD = true;
            }
        }

        if (isValidAltD === false) {
            alert("Invalid zip structure");
            altDDumpFile.value = "";
        };
    });
};


AldDUploadForm.onsubmit = function (e) {
    submitBtn.disabled = true;
    e.preventDefault();

    progressText.innerText = 'Submit in progress! Please, wait...';
    success.style.visibility = 'visible';


    const formData = new FormData(AldDUploadForm);
    setTimeout(function() {
        var xhr = new XMLHttpRequest();
        xhr.open(AldDUploadForm.method, AldDUploadForm.action, true);

        const progressTextRef = progressText;
        const successRef = success;

        xhr.onload = function() {
            progressTextRef.innerText = 'Submit successful! You can reload the page now and make another one.';
        };

        xhr.send(formData);

    }, (1000));
};


getFilePaths = function(zipContent, onComplete) {
    var altDZip = new JSZip();

    let filePaths = [];

    altDZip.loadAsync(zipContent).then(function() {

        file_dicts = Object.values(altDZip.files);

        for (const file_dict of file_dicts){
            filePaths.push(file_dict.name.toLowerCase());
        }

        onComplete(filePaths);
    }, function() {
            alert("Not a valid zip file");
            altDDumpFile.value = "";
       });
};


getAcceptablePathsToLogfile = function() {
    altDPathScanner = "log/logs";
    altDPathEchopac = "path/log/logs";
    insitePathScanner = "log";
    paths = [altDPathScanner, altDPathEchopac, insitePathScanner];

    acceptablePathsToLogfile = [];

    for (let i=0; i<paths.length; i++){
        acceptablePathsToLogfile.push(paths[i] + "/logfile.txt");

    }

    return acceptablePathsToLogfile;
};


isValidComment = function(comment, forbidden_regex) {
    return comment.match(forbidden_regex) === null;
};


comments.oninput = function() {
    const forbidden_regex = /[`^()\;:'"<>\{\}\[\]\\\/\&\$\#\|\%\?\@]/gi;
    if (isValidComment(this.value, forbidden_regex) === false) {
        alert("Removing invalid symbols from the comment");

        while (isValidComment(this.value, forbidden_regex) === false) {
            this.value = this.value.replace(forbidden_regex, '');
        };
    };
};
