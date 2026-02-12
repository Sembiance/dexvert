import {xu} from "xu";
import {Format} from "../../Format.js";

const WEAK_MAGIC = [
	// generic HTML
	"HyperText Markup Language with DOCTYPE", "HTML (Hyper Text Markup Language) Datei", "broken XHTML document text", /^Hyper[Tt]ext Markup Language/, /^X?HTML document/, /^text\/html/,
	/^fmt\/(96|97|98|99|100|102|103|471|1132)( |$)/,

	// app specific HTML
	"Microsoft HTML Application (HTA)"
];

const STRONG_MAGIC = [
	// generic
	"HTML start and end tags",

	// app specific HTML
	"IBrowse Hotlist / bookmark (v2)", "Internet Explorer history (v1-3)", "Internet Explorer bookmark", "Netscape Bookmark", "Expression Media template"
];

export class html extends Format
{
	name             = "Hypertext Markup Language File";
	website          = "http://fileformats.archiveteam.org/wiki/HTML";
	ext              = [".html", ".htm", ".xhtml", ".xht", ".hhk", ".hhc", ".hts", ".htx", ".shtml", ".phtml", ".hta", ".asp", ".aspx"];
	forbidExtMatch   = true;
	filename         = [/htm/];
	weakFilename     = true;
	mimeType         = "text/html";
	magic            = [...WEAK_MAGIC, ...STRONG_MAGIC];
	weakMagic        = WEAK_MAGIC;
	trustMagic       = true;
	idMeta           = ({macFileType, macFileCreator}) => (macFileType?.toLowerCase()==="html" && macFileCreator?.toLowerCase()==="html") || (macFileType==="HTML" && macFileCreator==="MOSS");
	confidenceAdjust = () => -10;	// Reduce by 10 since our magic is pretty weak, this allows other text formats that are less weak to match first, such as text/awk for sample text/awk/mib2html.awk
	untouched        = true;
	metaProvider     = ["text"];
	notes            = "I tried some ways I could relax this in order to properly detect HTML files that have no extension, but DOM parsers are really lenient and will parse almost anything as HTML. It is also CPU intensive.";
}
