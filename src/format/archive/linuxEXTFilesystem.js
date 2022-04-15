import {Format} from "../../Format.js";

export class linuxEXTFilesystem extends Format
{
	name           = "Linux Extended Filesystem";
	ext            = [".img", ".ext2", ".ext3", ".ext4"];
	forbidExtMatch = true;
	magic          = ["Linux extended file system image", /^Linux .*ext\d filesystem/];
	converters     = ["sevenZip"];
}
