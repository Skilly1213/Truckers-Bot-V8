
import sys, subprocess

text = " ".join(sys.argv[1:])

ps_script = '''
Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voices = $speak.GetInstalledVoices()
foreach ($v in $voices) {
    if ($v.VoiceInfo.Name -like "*Jenny*") {
        $speak.SelectVoice($v.VoiceInfo.Name)
    }
}
$speak.Speak("''' + text + '''")
'''

subprocess.run(["powershell","-Command", ps_script])
