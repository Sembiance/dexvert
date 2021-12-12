import {Format} from "../../Format.js";

export class ibmStoryboardDocument extends Format
{
	name           = "IBM Storyboard Text Maker Document";
	website        = "https://winworldpc.com/product/ibm-storyboard/";
	ext            = [".txm"];
	forbidExtMatch = true;
	magic          = ["IBM Storyboard screen Capture"];
	weakMagic      = true;
	notes          = "Storboard 1.0.1 text maker can open these, but I didn't see any way to convert them to TXT nor 'print' them. So we just use strings which is pretty good at getting the text out.";
	converters     = ["strings"];
}
