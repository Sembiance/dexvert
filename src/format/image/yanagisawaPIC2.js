import {Format} from "../../Format.js";

export class yanagisawaPIC2 extends Format
{
	name        = "Yanagisawa PIC2";
	website     = "http://fileformats.archiveteam.org/wiki/PIC2";
	ext         = [".p2"];
	magic       = ["PIC2 bitmap"];
	idMeta      = ({macFileType, macFileCreator}) => macFileType==="Pic2" && macFileCreator==="xPIC";
	weakMagic   = true;
	converters  = ["wuimg"];
	notes       = `There is a PIC2 plugin for 'xv' so maybe I could create a CLI program that leverages that to convert: https://github.com/DavidGriffith/xv/blob/master/xvpic2.c`;
}
