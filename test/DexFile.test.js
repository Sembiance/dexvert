import {assertStrictEquals} from "https://deno.land/std@0.111.0/testing/asserts.ts";
import {DexFile} from "../src/DexFile.js";

Deno.test("create", async () =>
{
	// single file, absolute path, root and clonse
	let a = await DexFile.create("/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
	const b = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", subPath : "some.big.txt.file.txt"});
	const c = b.clone();
	const d = b.clone();
	d.changeRoot("/some/random/dir");
	[a, b, c].forEach(o =>
	{
		assertStrictEquals(o.rel, "some.big.txt.file.txt");
		assertStrictEquals(o.root, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.absolute, "/mnt/compendium/DevLab/dexvert/test/files/some.big.txt.file.txt");
		assertStrictEquals(o.base, "some.big.txt.file.txt");
		assertStrictEquals(o.dir, "/mnt/compendium/DevLab/dexvert/test/files");
		assertStrictEquals(o.name, "some.big.txt.file");
		assertStrictEquals(o.ext, ".txt");
		assertStrictEquals(o.isFile, true);
		assertStrictEquals(o.isDirectory, false);
		assertStrictEquals(o.isSymlink, false);
		assertStrictEquals(o.size, 6);
		assertStrictEquals(o.ts.toString(), (new Date("2021-10-31T13:04:29.027Z")).toString());
		assertStrictEquals(o.preExt, ".some");
		assertStrictEquals(o.preName, "big.txt.file.txt");
	});

	// subDir file
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", subPath : "subDir/txt.b"});
	assertStrictEquals(a.rel, "subDir/txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts.toString(), (new Date("2021-10-31T13:04:44.995Z")).toString());
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");

	// symlink
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", subPath : "subDir/symlinkFile"});
	assertStrictEquals(a.rel, "subDir/symlinkFile");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/symlinkFile");
	assertStrictEquals(a.base, "symlinkFile");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "symlinkFile");
	assertStrictEquals(a.ext, "");
	assertStrictEquals(a.isFile, false);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, true);
	assertStrictEquals(a.ts.toString(), (new Date("2021-10-31T13:09:55.866Z")).toString());
	assertStrictEquals(a.preExt, "");
	assertStrictEquals(a.preName, "symlinkFile");

	// directory
	a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", subPath : "subDir/more_sub/third"});
	assertStrictEquals(a.rel, "subDir/more_sub/third");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub/third");
	assertStrictEquals(a.base, "third");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir/more_sub");
	assertStrictEquals(a.name, "third");
	assertStrictEquals(a.ext, "");
	assertStrictEquals(a.isFile, false);
	assertStrictEquals(a.isDirectory, true);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.ts.toString(), (new Date("2021-10-31T13:04:49.475Z")).toString());
	assertStrictEquals(a.preExt, "");
	assertStrictEquals(a.preName, "third");
});

Deno.test("changeRoot", async () =>
{
	const a = await DexFile.create({root : "/mnt/compendium/DevLab/dexvert/test/files/", subPath : "subDir/txt.b"});
	const b = a.clone();
	b.changeRoot("/tmp/dir/whatever/");

	// check that original was not changed
	assertStrictEquals(a.rel, "subDir/txt.b");
	assertStrictEquals(a.root, "/mnt/compendium/DevLab/dexvert/test/files");
	assertStrictEquals(a.absolute, "/mnt/compendium/DevLab/dexvert/test/files/subDir/txt.b");
	assertStrictEquals(a.base, "txt.b");
	assertStrictEquals(a.dir, "/mnt/compendium/DevLab/dexvert/test/files/subDir");
	assertStrictEquals(a.name, "txt");
	assertStrictEquals(a.ext, ".b");
	assertStrictEquals(a.isFile, true);
	assertStrictEquals(a.isDirectory, false);
	assertStrictEquals(a.isSymlink, false);
	assertStrictEquals(a.size, 8);
	assertStrictEquals(a.ts.toString(), (new Date("2021-10-31T13:04:44.995Z")).toString());
	assertStrictEquals(a.preExt, ".txt");
	assertStrictEquals(a.preName, "b");

	// check that clone was changed
	assertStrictEquals(b.rel, "subDir/txt.b");
	assertStrictEquals(b.root, "/tmp/dir/whatever");
	assertStrictEquals(b.absolute, "/tmp/dir/whatever/subDir/txt.b");
	assertStrictEquals(b.base, "txt.b");
	assertStrictEquals(b.dir, "/tmp/dir/whatever/subDir");
	assertStrictEquals(b.name, "txt");
	assertStrictEquals(b.ext, ".b");
	assertStrictEquals(b.isFile, true);
	assertStrictEquals(b.isDirectory, false);
	assertStrictEquals(b.isSymlink, false);
	assertStrictEquals(b.size, 8);
	assertStrictEquals(b.ts.toString(), (new Date("2021-10-31T13:04:44.995Z")).toString());
	assertStrictEquals(b.preExt, ".txt");
	assertStrictEquals(b.preName, "b");
});
