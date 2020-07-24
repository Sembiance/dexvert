"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

const C = {};

// A list of family types. Order is the secondary order they will be matched in the case of multiple 'types' of matches (magic, etc, filename) across multiple categories
C.FAMILIES = ["archive", "document", "audio", "database", "video", "image", "3d", "font", "other", "executable", "rom", "text"];

// A priority to use if a file matches multiple times within a single family
C.PRIORITY =
{
	TOP      : 0,
	HIGH     : 1,
	STANDARD : 2,
	LOW      : 3,
	VERYLOW  : 4
};

C.FORMAT_DIR_PATH = path.join(__dirname, "format");

C.UNOCONV_PORT = 27359;
C.DEXSERV_PORT = 17735;
C.DEXSERV_HOST = "localhost";
C.DEXSERV_OK_RESPONSE = "a-ok";

C.TEXT_MAGIC = ["ASCII text", "ISO-8859 text", "UTF-8 Unicode text", "Non-ISO extended-ASCII text", "ReStructuredText file", "International EBCDIC text", "UTF-8 Unicode text"];
C.GENERIC_MAGIC = [/^data$/, /^very short file \(no magic\)$/, /^null bytes$/];

// Matches the given value against the matcher. If 'matcher' is a string, then value just needs to start with matcher, unless fullStringMatch is set then the entire string must be a case insensitive match. If 'matcher' is a regexp, it must regex match value.
C.flexMatch = function flexMatch(value, matcher, fullStringMatch)
{
	return ((typeof matcher==="string" && (fullStringMatch ? (value.toLowerCase()===matcher.toLowerCase()) : value.toLowerCase().startsWith(matcher.toLowerCase()))) || (matcher instanceof RegExp && value.match(matcher)));
};

module.exports = C;
