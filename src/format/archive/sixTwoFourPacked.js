import {Format} from "../../Format.js";

export class sixTwoFourPacked extends Format
{
	name        = "624 Packed";
	magic       = ["Packer: Six-2-Fou", "Six-2-Four (624) packed DOS Command"];
	packed      = true;
	unsupported = true;
	notes       = "No known unpacker. Source code for the program, including assembly for decompression available here: https://discmaster.textfiles.com/browse/20219/hornet.scene.org%20FTP%2011-25-2012.zip/hornet.scene.org%20FTP%2011-25-2012/code/compress/plp_624.zip";
}
