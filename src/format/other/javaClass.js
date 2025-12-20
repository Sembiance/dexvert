import {Format} from "../../Format.js";

export class javaClass extends Format
{
	name           = "Java Class File";
	website        = "http://fileformats.archiveteam.org/wiki/Java_bytecode";
	ext            = [".class"];
	forbidExtMatch = true;
	magic          = ["Java Compiled Object Code", "compiled Java class data", "Java bytecode", "Format: Java Class File", "Kompilierter Java Bytecode", "application/x-java", "Format: Java Class", /^x-fmt\/415( |$)/];
	weakMagic      = ["Kompilierter Java Bytecode"];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="Clss" && ["CWIE", "JAVA", "MWZP"].includes(macFileCreator)) || (["clss", "CLAS"].includes(macFileType) && ["java", "Rstr"].includes(macFileCreator));
	converters     = ["fernflower"];	// Others: https://github.com/neocanable/garlic   and  https://github.com/Vineflower/vineflower/releases
}
