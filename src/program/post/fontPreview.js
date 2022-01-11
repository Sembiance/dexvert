import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class fontPreview extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	bin     = "inkscape";
	flags = {
		family : "Which font family, REQUIRED"
	};
	args    = async r =>
	{
		r.svgPreviewFilePath = await fileUtil.genTempPath(r.f.root, ".svg");

		await Deno.writeTextFile(r.svgPreviewFilePath, `<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <defs>
        <style>
			@font-face{font-family:&quot;${r.flags.family.toString().escapeXML()}&quot;;src:url(&quot;${r.inFile({absolute : true}).escapeXML()}&quot;)}
        </style>
    </defs>
    <g>
		<text font-size="18pt" font-family="${r.flags.family.toString().escapeXML()}, Arial">
			<tspan x="0" y="18pt">abcdefghijklmnopqrstuvwxyz</tspan>
			<tspan x="0" dy="26pt">ABCDEFGHIJKLMNOPQRSTUVWXYZ</tspan>
			<tspan x="0" dy="26pt">0123456789\`~!@#$%^&amp;*()-_+=&gt;,&lt;.[]{}|\\:;"'/?</tspan>
			<tspan x="0" dy="26pt"> ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿</tspan>
			<tspan x="0" dy="26pt">ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß</tspan>
			<tspan x="0" dy="26pt">àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ</tspan>
		</text>
		<text dy="190pt" font-size="18pt" font-family="${r.flags.family.toString().escapeXML()}, Arial">
			<tspan x="0" y="0">12</tspan><tspan x="28pt" font-size="12pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="26pt">18</tspan><tspan x="28pt" font-size="18pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="30pt">24</tspan><tspan x="28pt" font-size="24pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="36pt">36</tspan><tspan x="28pt" font-size="36pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="48pt">48</tspan><tspan x="28pt" font-size="48pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="60pt">60</tspan><tspan x="28pt" font-size="60pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="72pt">72</tspan><tspan x="28pt" font-size="72pt">The quick brown fox jumps over the lazy dog.</tspan>
		</text>
    </g>
</svg>`);

		return [`--actions=export-area-drawing; export-filename:${await r.outFile("out.png", {absolute : true})}; export-do;`, r.svgPreviewFilePath];
	};
	renameOut  = true;
}
