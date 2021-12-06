import {Format} from "../../Format.js";

export class tss extends Format
{
	name        = "T'SoundSystem Source Module";
	ext         = [".tss"];
	magic       = ["T'SoundSystem Source"];
	unsupported = true;
}
