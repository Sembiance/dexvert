import {Format} from "../../Format.js";

export class zyxelVoice extends Format
{
	name           = "ZyXEL Voice Data";
	ext            = [".zvd", ".zyx"];
	forbidExtMatch = true;
	magic          = ["ZyXEL voice data", "ZyXEL Voice Format audio", /^fmt\/1674( |$)/];
	converters     = ["vibe2wav[renameOut]"];
}
