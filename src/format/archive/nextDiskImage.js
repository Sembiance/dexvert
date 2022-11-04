import {Format} from "../../Format.js";

export class nextDiskImage extends Format
{
	name           = "NeXT Disk Image";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = [/^NeXT disk image$/];
	converters     = ["uniso[nextstep]"];
}
