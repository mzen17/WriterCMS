/*
Code for spellchecker plugin for tinymce
This plugin exploits browser spellcheck and force-enables spell check on TinyMCE
which for some reason, doesn't provide an API.
It provides a simple spell check and highlights words that need help.
*/

function enableSpellCheck() {
    console.log("STS")

    const iframe = document.getElementById('pg_content_ifr');
    if (iframe && iframe.contentDocument) {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const tinymceBox = iframeDoc.getElementById('tinymce');

        if (tinymceBox) {
            console.log("FND")
            tinymceBox.spellcheck = true;
    
        }

    }
}

function disableSpellCheck() {

    const iframe = document.getElementById('pg_content_ifr');
    if (iframe && iframe.contentDocument) {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
        const tinymceBox = iframeDoc.getElementById('tinymce');

        if (tinymceBox) {
            console.log("FND")
            tinymceBox.spellcheck = false;
    
        }

    }
}


tinymce.PluginManager.add('spellchecker', (editor, url) => {
    editor.ui.registry.addMenuItem('enable-spell-check', {
        text: 'Enable Spell Check',
        onAction: () => enableSpellCheck()
    });

    editor.ui.registry.addMenuItem('disable-spell-check', {
        text: 'Disable Spell Check',
        onAction: () => disableSpellCheck()
    });
  /* Return the metadata for the help plugin */
  return {
    getMetadata: () => ({
      name: 'OSS Spellchecker for TinyMCE via browser.',
      url: 'https://mzen.dev'
    })
  };
});