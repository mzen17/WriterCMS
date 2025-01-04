/*
Code for spellchecker plugin for tinymce
This plugin is currently extremely slow and buggy.

It provides a simple spell check and highlights words that need help.
*/

function clearAnnotations() {
    var data = tinymce.activeEditor.getContent(); // String

    data = data.replace(/❉.*?❈/g, '')
    tinymce.activeEditor.setContent(data)
}

function suggestSingle() {
    var dictionary = new Typo("en-US", false, false, { dictionaryPath: "/static/dicts" })

    let collect = tinyMCE.activeEditor.selection.getContent();
    var array_of_suggestions = dictionary.suggest(collect);

    tinyMCE.activeEditor.selection.setContent(collect + "|" + array_of_suggestions);
}

function placeAnnotations(list2drop, listOfCorr) {
    var data = tinymce.activeEditor.getContent(); // String
    list2drop = [...new Set(list2drop)];
    function replStr(s) {
        let lcStr = ""

        if (s in listOfCorr) {
            lcStr = listOfCorr[s];
        }

        prefx = '❉<span style="color: rgb(0, 0, 0); background-color: rgb(224, 62, 45);">❈'
        endfx = '❉</span><span style="background-color: rgb(45, 194, 107);">' + lcStr + "</span>❈"
        
        let filter = RegExp(`[^a-zA-Z0-9'-]${s}[^a-zA-Z0-9'-]`)
        let value = data.match(filter);

        let initChar = "";
        let endChar = "";

        if (value !== null) {
            let tstr = value[0]
            initChar = tstr.charAt(0);
            endChar = tstr.charAt(tstr.length - 1);
        }

        data = data.replace(filter,  (initChar + prefx + s + endfx + endChar) )
    }
    list2drop.forEach(replStr)
    tinymce.activeEditor.setContent(data)
}

// Fast -- boolean (suggestions or no), extrawords -- List[str]
async function spellcheckBlob(fast) {
    if (typeof getDictLocation !== "function") { 
        alert("This will break, because dictionary_path was not defined. Please contact site owner/maintainer.")
    }

    clearAnnotations()

    var dictionary = new Typo("en-US", false, false, { dictionaryPath: getDictLocation() })

    if (typeof getExtraDict === "function") { 
        extraWords = await getExtraDict();

        function append2dict(word) {
            console.log("Special Add: " + word);
            dictionary.dictionaryTable[word] = []
            dictionary.dictionaryTable[word].push([]);
        }
        extraWords.forEach(append2dict);
    }

    var data = tinymce.activeEditor.getContent(); // String

    const pattern = />[^<]*</g;
    const matches = data.match(pattern);
    const result = matches.map(match => match.slice(1, -1));

    let wrdlist = []
    let correct = {}

    function appendToWrdList(s) {
        const resultarr = s.split(' ');

        function toss(s2) {
            let containsDash = s2.includes("-")
            let containsApos = s2.includes("'")

            let fixStr = s2.replace(/&nbsp;/g, '');
            fixStr = fixStr.replace(/&rdquo;/g, '');
            fixStr = fixStr.replace(/&ldquo;/g, '');
            fixStr = fixStr.replace(/\n/g, '');

            fixStr = fixStr.replace(/[^\w\s'-]/g, '');
            fixStr = fixStr.replace(/\n/g, '');

            fixStr = fixStr.replace(/^[-']|[-']$/g, '');

            if ( fixStr !== "" && !dictionary.check(fixStr)) { 
                works = false

                function chkWork(s3) {
                    works = works && dictionary.check(s3);
                }

                if (containsDash) {
                    blob = fixStr.split("-")
                    works = true;
                    blob.forEach(chkWork)
                } else if(containsApos) {
                    blob = fixStr.split("'")
                    works = true;
                    blob.forEach(chkWork)
                }

                if( !works ) {
                    wrdlist.push(fixStr);
                    
                    if (!fast && !(fixStr in correct)) {
                        var array_of_suggestions = dictionary.suggest(fixStr);
                        correct[fixStr] = array_of_suggestions
                    }
                    console.log("Finished correcting: " + fixStr)
                }
            }
        }
        resultarr.forEach(toss);
    }
    result.forEach(appendToWrdList);

    placeAnnotations(wrdlist, correct);
}

function addWord2Dict() {
    let collect = tinyMCE.activeEditor.selection.getContent();
    words2append = collect.split(" ");

    if (typeof addWordToUserDict === "function") { 
        words2append.forEach(addWordToUserDict);
    }
}

tinymce.PluginManager.add('spellchecker', (editor, url) => {
    editor.ui.registry.addMenuItem('spell-check-fast', {
        text: 'Spell Check',
        onAction: () => spellcheckBlob(true)
    });

    editor.ui.registry.addMenuItem('spell-check', {
        text: 'Spell Check Suggestions (Very Slow)',
        onAction: () => spellcheckBlob(false)
    });

    editor.ui.registry.addMenuItem('spell-single', {
        text: 'Spelling Suggest Word',
        onAction: () => suggestSingle()
    });

    editor.ui.registry.addMenuItem('add-word', {
        text: 'Add word to dictionary',
        onAction: () => addWord2Dict()
    });

    editor.ui.registry.addMenuItem('clear-annotations', {
        text: 'Clear Annotations',
        onAction: () => clearAnnotations()
    });

  /* Return the metadata for the help plugin */
  return {
    getMetadata: () => ({
      name: 'OSS Spellchecker for TinyMCE',
      url: 'https://mzen.dev'
    })
  };
});