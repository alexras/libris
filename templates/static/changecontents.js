// Adapted from http://forums.sureshkumar.net/web-designing-development-promotion-seo/38245-html-javascript-editable-tables-sample-code.html

function changeContent(tableCell, paperName, fieldName)
{
    var submitFunc = "submitNewName(this, '" + paperName + "', '" +
        fieldName + "');";
    var keyDownFunc = "if (window.event.keyCode == 13) this.blur();";

    if (tableCell.innerHTML.substring(0, 6) != "<input") {
        tableCell.innerHTML = "<input type=text name=newname " +
            "onBlur=\"javascript:" + submitFunc + "\" onKeyDown=\"javascript:" +
            keyDownFunc + "\" value=\"" + tableCell.innerHTML + "\">";
    }
    tableCell.firstChild.focus();
}

function submitNewName(textField, paperName, fieldName)
{
    post_data = {
        "field_name" : fieldName,
        "new_value" : textField.value
    }

    $.post('/edit_metadata/' + paperName, post_data, function(data) {
        textField.parentNode.innerHTML = data;
    })
        .error(function() {
            alert("Edit failed.");
            textField.parentNode.innerHTML = textField.value;
        });
}
