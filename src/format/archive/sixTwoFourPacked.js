import {Format} from "../../Format.js";

export class sixTwoFourPacked extends Format
{
	name       = "624 Packed";
	magic      = ["Packer: Six-2-Fou", "Six-2-Four (624) packed DOS Command"];
	packed     = true;
	converters = ["cup386"];
}
