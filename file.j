.class public A
.super java/lang/Object
.method public static factorial(I)I
.limit stack 3
.limit locals 2
iload_0
istore_1
iload_0
iconst_1
if_icmple LABEL0x1
iload_1
iload_0
iconst_1
isub
invokestatic A/factorial(I)I
imul
istore_1
LABEL0x1:
iload_1
ireturn
.end method

.method public static main([Ljava/lang/String;)V
.limit stack 2
.limit locals 2
iconst_5
invokestatic A/factorial(I)I
istore_1
getstatic java/lang/System/out Ljava/io/PrintStream;
iload_1
invokevirtual java/io/PrintStream/println(I)V
return
.end method

