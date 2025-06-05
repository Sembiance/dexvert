import {Program} from "../../Program.js";

export class fernflower extends Program
{
	website   = "https://mvnrepository.com/artifact/com.jetbrains.intellij.java/java-decompiler-engine";
	package   = "dev-util/fernflower";
	bin       = "fernflower";
	args      = r => ["-ren=1", "-dgs=1", r.inFile(), r.outDir()];	// Usage: https://the.bytecode.club/fernflower.txt
	renameOut = true;
}
