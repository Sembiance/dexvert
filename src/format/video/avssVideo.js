import {Format} from "../../Format.js";

export class avssVideo extends Format
{
	name           = "AVSS Video";
	website        = "http://ohlandl.ipv7.net/video/actionmedia.html";
	ext            = [".avs"];
	forbidExtMatch = true;
	magic          = ["AVSS Video"];
	converters     = ["vibe2avi"];
}
