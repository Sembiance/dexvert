import {Format} from "../../Format.js";

export class zyxelVoice extends Format
{
	name        = "ZyXEL Voice Data";
	ext         = [".zvd", ".zyx"];
	magic       = ["ZyXEL voice data", "ZyXEL Voice Format audio"];
	unsupported = true;
}
