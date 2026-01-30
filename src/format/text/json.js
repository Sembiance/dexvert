import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "../../Format.js";

export class json extends Format
{
	name             = "JavaScript Object Notation";
	website          = "http://fileformats.archiveteam.org/wiki/JSON";
	ext              = [".json"];
	magic            = [
		// generic
		"JSON text data",

		// app specific
		"Chrome Bookmarks", "Firefox bookmark (JavaScript Object Notation)", "Xcode Asset Catalog", /^Max Patch$/, "application/schema+json", "Node.js Package Manifest", /^Unreal Engine (Plugin|Project)$/, /^fmt\/1311( |$)/
	];
	weakMagic        = true;
	mimeType         = "application/json";
	untouched        = dexState => !!dexState.meta.type;
	confidenceAdjust = (inputFile, matchType, curConfidence) => -(curConfidence-60);	// JSON is used for other formats (such as image/lottie) so we should always process same match types with a lower priority
	metaProvider     = ["text"];
	meta             = async inputFile =>
	{
		// anything 10MB or larger skip parsing
		if(inputFile.size>xu.MB*10)
			return {};

		const result = xu.parseJSON(await fileUtil.readTextFile(inputFile.absolute));
		if(!result)
			return {};

		const meta = {};
		if(Array.isArray(result))
		{
			meta.type = "array";
			meta.entryCount = result.length;
		}
		else if(Object.isObject(result))
		{
			meta.type = "object";
			meta.keyCount = Object.keys(result).length;
		}
		else
		{
			meta.type = typeof result;
		}

		return meta;
	};
}
