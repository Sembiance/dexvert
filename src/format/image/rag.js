import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class rag extends Format
{
	name           = "RAG-D";
	website        = "http://fileformats.archiveteam.org/wiki/RAG-D";
	ext            = [".rag", ".ragc"];
	forbidExtMatch = [".ragc"];
	safeExt        = async dexState =>
	{
		if(dexState.f.input.size<22)
			return ".rag";
		// So, the standard RAG-D format is what recoil converts. However discmaster has never encountered any of these in the wild
		// What it has encountered is a modified version of RAG-D that a program called Music Compile 2 uses
		// 99% of the files are able to be identified with an 0xFF byte check at offset 22
		// However 1 regular RAG file (rraa9.rag) also has this byte byte it's not a music compile 2 file
		// Recoil decided it was best to have to explicitly opt into the Music Compile 2 variant with a .ragc extensions
		// However here we are gonna automate that since 100% of the files encountered by discmaster are the music compile 2 variant
		// See tickets for more details: https://sourceforge.net/p/recoil/bugs/74/  and  https://sourceforge.net/p/recoil/bugs/93/
		const headerBuf = await fileUtil.readFileBytes(dexState.f.input.absolute, 24);
		return headerBuf[22]===0xFF ? ".ragc" : ".rag";
	};
	magic      = ["RAG-D bitmap"];
	converters = ["recoil2png[format:RAG,RAGC]"];
}
