/*
 * parapy.js
 * ~~~~~~~~~~~
 *
 * ParaPy JavaScript extension to Sphinx for all documentation
 *
 * :copyright: Copyright 2014-2016 by Reinier van Dijk
 *
 * This script does several things:
 *
 * 1. add buttons to <h2> elements (inheritance, private)
 *    except for Required Inputs (always show all)
 * 2. prepend <dl> elements with symbols (inheritance, private)
 * 3. strip (return) type information from SPhinx tables and add them
 *    to signature of attribute / method
 * 4. collapse <dl> elements.
 */

var collapseAllOnReady = false;
var showInhOnReady = true;
var showPrvOnReady = false;
var hideDocUtilsTableOnRtypeOnly = false;
var toggleSpeed = 400;
var slidingSpeed = 400;
var headerWrp = "<div class='hwrap1'><div class='hwrap2'></div></div>";
var defaultValueSeparator = "=";
var removeDefaultValueMeta = true;
var validMemberClasses = ["slot", "method", "classmethod", "staticmethod"];
var numberOfValidMemberClasses = validMemberClasses.length;

var imgPathPrefix = "_static/";
var imgExpPath = imgPathPrefix + "parapy_expand_all.svg";
var imgColPath = imgPathPrefix + "parapy_collapse_all.svg";
var imgDiaPath = imgPathPrefix + "parapy_classdiag.svg";
var imgPrvPath = imgPathPrefix + "parapy_private.svg";
var imgInhPath = imgPathPrefix + "parapy_inherited.svg";
var imgOvePath = imgPathPrefix + "parapy_overridden.svg";

function jq(hash) {
    return hash.replace(/(:|\.|\[|]|,)/g, "\\$1");
}

/**
 * append images to <hi> element and wrap inside double-nested div.
 * @param {HTMLElement} header - <hi> element to append images to and wrap
 * @param {Array} imgArray - array of <img> objects.
 * @returns {jQuery} - <div> element wrapping header.
 */
function initHeader(header, imgArray) {
    var div = $(header).wrap(headerWrp).parent().parent();
    for (var i = 0; i < imgArray.length; i++) {
        $(header).after(imgArray[i]);
    }
    $(div).addClass($(header).attr("class"));
    return div
}

/**
 * Return <img> for appending after headers.
 * @param {string} src - 'src' attribute.
 * @param {string} cls - 'class' attribute.
 * @param {string} title - title to show on hover.
 * @returns {jQuery} - <img> element.
 */
function makeHeaderImage(src, cls, title) {
    return $('<img>', {src: src, class: cls, title: title});
}

function initClassHeader($dl) {
    var $prevElmt = $dl.prev();
    var $h2 = $prevElmt;
    var imgArray = [];
    if ($prevElmt.hasClass("graphviz")) {
        // $prevElmt is <p class='graphviz'>
        var imgDia = makeHeaderImage(imgDiaPath, "dia",
            "show inheritance diagram.").click(function () {
                $prevElmt.toggle(toggleSpeed);
            });
        imgArray.push(imgDia);
        $h2 = $prevElmt.prev();
        $prevElmt.hide();
    }

    return initHeader($h2, [imgDia]);

}

function initMemberCategoryHeader(header) {

    var imgExp = makeHeaderImage(imgExpPath, "expand_all",
        "expand all docstrings").click(function () {
            expandAll(wrappingDiv, toggleSpeed)
        });

    var imgCol = makeHeaderImage(imgColPath, "collapse_all",
        "collapse all docstrings").click(function () {
            collapseAll(wrappingDiv, toggleSpeed)
        });

    var imgInh = makeHeaderImage(imgInhPath, "inherited",
        "toggle visibility of inherited attributes").click(function () {
            $(this).toggleClass("down");
            var showInh = $(this).hasClass("down");
            var showPrv = imgPrv.hasClass("down");
            updateVisibility(wrappingDiv, showInh, showPrv, slidingSpeed);
        });

    var imgPrv = makeHeaderImage(imgPrvPath, "private",
        "toggle visibility of private attributes").click(function () {
            $(this).toggleClass("down");
            var showInh = imgInh.hasClass("down");
            var showPrv = $(this).hasClass("down");
            updateVisibility(wrappingDiv, showInh, showPrv, slidingSpeed);
        });

    var imgArray = [imgExp, imgCol, imgInh, imgPrv];
    var wrappingDiv = initHeader(header, imgArray);
    var is_input = $(header).text() == "Required Inputs" || $(header).text() == "Optional Inputs";
    var header_text = $(header).text();
    var showInh = showInhOnReady;
    var showPrv = showPrvOnReady;

    if (header_text == "Required Inputs" || header_text == "Optional Inputs") {
        showInh = true;
    }
    if (header_text == "Required Inputs") {
        showPrv = true;
    }

    var hasInh = $(wrappingDiv).nextUntil(".category", "dl.inherited").length > 0;
    var hasPrv = $(wrappingDiv).nextUntil(".category", "dl.private").length > 0;

    if (!hasInh) {
        imgInh.hide()
    }
    if (!hasPrv) {
        imgPrv.hide()
    }
    if (showInh) {
        $(imgInh).toggleClass("down")
    }
    if (showPrv) {
        $(imgPrv).toggleClass("down")
    }
    if (!showInh || !showPrv) {
        updateVisibility(wrappingDiv, showInh, showPrv, 0);
    }
    if (collapseAllOnReady) {
        collapseAll(wrappingDiv, 0)
    }

    return wrappingDiv
}

function expandDD(dd, speed, callback) {
    if ($(dd).hasClass("collapsed")) {
        toggleDD(dd, speed, callback)
    }
}

function collapseDD(dd, speed, callback) {
    if (!$(dd).hasClass("collapsed")) {
        toggleDD(dd, speed, callback)
    }
}

function toggleDD(dd, speed, callback) {
    $(dd).toggle(speed);
    $(dd).toggleClass("collapsed");
    if (callback) {
        callback();
    }
}

function expandAll(header, speed, callback) {
    $(header).nextUntil(".category", "dl").each(function () {
        expandDD($("> dd", $(this)), speed, callback);
    });
    return false;
}

function collapseAll(header, speed, callback) {
    $(header).nextUntil(".category", "dl").each(function () {
        collapseDD($("> dd", $(this)), speed, callback);
    });
    return false;
}

function updateVisibility(header, showInh, showPrv, speed) {
    var filter = "dl.inherited, dl.private";
    $(header).nextUntil(".category", filter).each(function () {
        var $dl = $(this);
        if ((!$dl.hasClass("inherited") || showInh) &&
            (!$dl.hasClass("private") || showPrv)) {
            $dl.slideDown(speed);
        } else {
            $dl.slideUp(speed);
        }
    })
}

function hasValidMemberClass($dl) {
    for (var i = 0; i < numberOfValidMemberClasses; i++) {
        if ($dl.hasClass(validMemberClasses[i])) {
            return true;
        }
    }
    return false;
}

function getReturnType(dl, isInput) {

    var rtype = undefined;
    var $table = $(" > dd > table.docutils", dl);

    if ($table.length) {
        var rtypeKeys = ["Return type:"];
        if (isInput) {
            rtypeKeys.push("Type:");
        }
        var rows = $table.find("tbody").children("tr");
        rows.each(function () {
            var txt = $(this).find("th").text();
            if ($.inArray(txt, rtypeKeys) >= 0) {
                rtype = $("td", this).text();
                if (hideDocUtilsTableOnRtypeOnly && rows.length == 1) {
                    $table.hide();
                }
            }
        });
    }
    return rtype;
}

// returns undefined if no default value is present.
function getDefaultValue(dl, isInput) {
    var defaultValue;
    if (isInput) {
        var $prev = $(dl).prev();
        if ($prev.is("meta") && $prev.hasClass("default")) {
            defaultValue = $prev.attr("value");
            if (removeDefaultValueMeta) {
                $prev.remove();
            }
        }
    }
    return defaultValue
}

function appendMemberSignature(dl, rtype, defaultValue, isInput) {
    var $last = $(dl).find("> dt").children().last();
    if ($last.is("a")) {
        $last = $last.prev();
    }

    if (rtype) {
        var rtypeSeparator = "→";
        if (isInput) {
            rtypeSeparator = "←"
        }
        $last.after($('<code>', {
            class: "rtypedecl",
            text: rtype
        }));
        $last.after($('<span>', {
            class: "rtypeseparator",
            text: rtypeSeparator
        }));
    }

    if (defaultValue) {
        $last.after($('<code>', {
            class: "defaultvaluedecl"
        }).append(defaultValue));
        $last.after($('<span>', {
            class: "defaultvalueseparator",
            text: defaultValueSeparator
        }));
    }
}

function prependMemberImage(dl, src, title) {
    var img = $('<img>', {class: "memberSymbol", src: src, title: title});
    $(dl).prepend(img);
    return img
}

function prependMemberImages(dl) {
    var $dl = $(dl);
    if ($dl.hasClass("inherited")) {
        prependMemberImage($dl, imgInhPath, "inherited from ancestor classes");
    }
    if ($dl.hasClass("overridden")) {
        prependMemberImage($dl, imgOvePath, "overridden from ancestor classes");
    }
    if ($dl.hasClass("private")) {
        prependMemberImage($dl, imgPrvPath, "private attribute");
    }
}

function addToggleBehavior($dl) {
    $("> dt > code.descname", $dl).click(function () {
        toggleDD($(this).parent().next(), toggleSpeed);
    });
}

$(document).ready(function () {

    $("dl.class").each(function () {
        var $classDL = $(this);
        initClassHeader($classDL);

        $("> dd > .category", $classDL).each(function () {
            initMemberCategoryHeader($(this));
        });

        $("> dd > dl", $classDL).each(function () {
            var $memberDL = $(this);
            if (hasValidMemberClass($memberDL)) {
                var isInput = $memberDL.hasClass("input");
                var rtype = getReturnType($memberDL, isInput);
                var defaultValue = getDefaultValue($memberDL, isInput);

                prependMemberImages($memberDL);
                appendMemberSignature($memberDL, rtype, defaultValue, isInput);
                addToggleBehavior($memberDL);
            }
            else {
                console.error(
                    "This <dl> has a Sphinx class that is not supported",
                    $memberDL);
                $memberDL.hide();
            }
        });
    });

    // if window location hash points to a class member, expand it.
    if (window.location.hash) {
        var $dtCandidate = $("dl.class > dd > dl > dt" + jq(window.location.hash));
        if ($dtCandidate.length) {
            expandDD($dtCandidate.next(), toggleSpeed,
                function () {
                    $(window).scrollTop($dtCandidate.offset().top)
                });
        }
    }
});
