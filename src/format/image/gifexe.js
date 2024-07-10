import {Format} from "../../Format.js";

const _GIFEXE_MAGIC = ["16bit DOS EXE GIFEXE"];
export {_GIFEXE_MAGIC};

export class gifexe extends Format
{
	name       = "GIFEXE Image";
	website    = "http://fileformats.archiveteam.org/wiki/GIFEXE";
	magic      = _GIFEXE_MAGIC;
	priority   = this.PRIORITY.HIGH;
	converters = ["unp -> foremost", "cup386 -> foremost"];
}
