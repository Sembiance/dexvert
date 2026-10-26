import {Format} from "../../Format.js";

export class screenCamVideo extends Format
{
	name           = "ScreenCam Video";
	website        = "https://wiki.multimedia.cx/index.php/SCM";
	ext            = [".scm"];
	forbidExtMatch = true;
	magic          = ["ScreenCam video", "Lotus Screen Cam Datei", /^fmt\/1938( |$)/];
	converters     = ["vibe2avi"];
}
