## Miniconda

> Based on [Katie Kodes' blog](https://katiekodes.com/setup-python-windows-miniconda/#installing-miniconda--running-a-python-program)

### 1. Run the Miniconda installer
Double-click the ".exe" file to run setup. Click “Next,” then click “I Agree” on the following screen.

<figure markdown>
  ![windows_1](/assets/images/installation/windows_1.png){ width="100%" }
</figure>


### 2. Choose "just me" or "all users"
I'm going to install this for "just me", because I don’t have admin rights to install software on my corporate PC.

My choice here influences whether the installer suggests installing the program under:

`C:\Users\MY_USERNAME\AppData\Local\Continuum\miniconda3` (just me), or
`C:\ProgramData\Miniconda3` (all users)

<figure markdown>
  ![windows_2](/assets/images/installation/windows_2.png){ width="100%" }
</figure>

### 3. Installation folder
It bothers me to forget when software is installed in my `\AppData\Local\` hidden folders, so I am going to manually change the installation path on the next screen to `C:\Users\MY_USERNAME\Documents\ProgramFilesForSoftwareHatingSpaces\Continuum\miniconda3`.

(Also, I already have another copy of Anaconda on my system, and I think I might have let it install there, and I don't want to mess it up while writing this blog post.)

Yes, I called that folder "`ProgramFilesForSoftwareHatingSpaces`" – I was feeling a bit pouty when Anaconda complained about my "Program Files" folder I'd set up under "My Documents".
<figure markdown>
  ![windows_3](/assets/images/installation/windows_3.png){ width="100%" }
</figure>


### 4. Options
Next, the installer is going to ask me whether I want to do either of two things.

- Add "Anaconda" to my "PATH" environment variable. It says not to do it right in the installer text, so I'm going to leave it un-checked.

- Register "Anaconda" as my "default Python 3.7" environment. This comes checked, and they recommend it, but I already have Python installed elsewhere on my computer. I'm just installing this to blog about it. So I am going to un-check it. You will probably want to leave it checked.

Now I'll click "Install".

<figure markdown>
  ![windows_4](/assets/images/installation/windows_4.png){ width="100%" }
</figure>

### 5. While it runs
The installer takes a few minutes while it dumps thousands of small files onto your hard drive.

!!! note
    Q: Why so many files?

    A: Your computer doesn’t naturally understand Python commands.

    At a really low level, it understand commands in its “assembly language” (which you wouldn’t want to have to write by hand).

    All Windows computers are shipped understanding a language called “C” (which, if you don’t want to become a professional programmer, you probably still wouldn’t want to have to write by hand).

    Lots of support programs written in "C" teach your Windows computer how to understand commands written in "Python" (presuming you, or a program like an "IDE" acting on your behalf, tell Windows where exactly you installed your software that can help parse these commands – for me, that would be `C:\Users\MY_USERNAME\Documents\ProgramFilesForSoftwareHatingSpaces\Continuum\miniconda3\python.exe`).

<figure markdown>
  ![windows_5](/assets/images/installation/windows_5.png){ width="100%" }
</figure>


### 6. Finishing
When it says "Completed", click "Next".

Leave the "learn more" boxes checked, or un-check them, as you prefer, and click "Finish".

(The second checkbox brings you here; the first just brings you to Anaconda's website.)

<figure markdown>
  ![windows_6](/assets/images/installation/windows_6.png){ width="100%" }
</figure>
