import {xu} from "xu";
import {initDOMParser, DOMParser} from "denoLandX";
import {formats} from "../src/format/formats.js";
import {runUtil} from "xutil";

const IGNORED_MIMES =
[
	// Handled natively
	"image/apng", "image/vnd.mozilla.apng",

	// Handled by another mime type
	"image/jpeg2000",
	"image/x-eps",
	"image/x-stos-picturepacker",
	"image/x-portable-anymap",
	
	// Handled by another program
	"application/eps", "application/postscript", "application/x-eps", "image/eps",
	"application/json",
	"application/x-rar", "application/x-tar", "application/zip", "application/x-7z-compressed",
	"video/x-anim",

	// Already Handled, mime aliases
	"application/fits", "image/x-sony-srf", "image/x-sony-sr2",

	// Chosen not to handle at all
	"application/x-doom-wad",
	"application/x-cb7", "application/x-cba", "application/vnd.comicbook-rar", "application/x-cbr", "application/x-cbt", "application/vnd.comicbook+zip", "application/x-cbz",

	// Document formats
	"application/oxps", "application/vnd.ms-xpsdocument",
	"application/pdf", "application/x-pdf",
	"image/vnd.djvu",

	// Modern formats
	"image/x-fuif",
	"image/x-pik",
	"image/jpx"
];

const supportedMimeTypes = Object.values(formats).map(format => format.mimeType).filter(v => !!v).unique();

const formatsHTMLRaw = await (await fetch("http://snisurset.net/code/abydos/supported.html")).text();

const {stdout : programMimeTypesRaw} = await runUtil.run("abydosconvert", ["--list"]);
const programMimeTypes = programMimeTypesRaw.trim().split("\n").subtractAll(supportedMimeTypes).subtractAll(IGNORED_MIMES);

let unsupportedCount = 0;
await initDOMParser();
const doc = new DOMParser().parseFromString(formatsHTMLRaw, "text/html");
Array.from(doc.querySelectorAll("table.grid tr")).forEach(row =>
{
	const cells = Array.from(row.querySelectorAll("td"), cell => (cell.textContent || "").trim());
	if(cells.length!==8 || cells[1].length===0 || cells[3].toLowerCase()==="no")
		return;
	
	const mimeTypes = cells[1].split(",").map(v => v.trim()).subtractAll(IGNORED_MIMES);
	programMimeTypes.filterInPlace(mimeType => !mimeTypes.includes(mimeType));
	if(mimeTypes.length===0 || mimeTypes.some(mimeType => supportedMimeTypes.includes(mimeType)))
		return;

	console.log(`Unsupported abydos format: ${cells[0]} ${mimeTypes.join(", ")}`);
	unsupportedCount++;
});

for(const programMimeType of programMimeTypes)
{
	console.log(`Unsupported abydos format: ${programMimeType}`);
	unsupportedCount++;
}

console.log(`\nUnsupported count: ${unsupportedCount}`);

/*
tiptoe(
	function downloadWebPage()
	{
		fileUtil.glob(path.join(__dirname, "..", "src", "format"), "** /*.js", {nodir : true}, this.parallel());
	},
	function checkFormats(formatsHTMLRaw, imageFormatFilePaths)
	{
		const supportedMimeTypes = imageFormatFilePaths.map(imageFormatFilePath => (require(imageFormatFilePath).meta || {}).mimeType).filterEmpty();


		this();
	},
	XU.FINISH
);
*/
