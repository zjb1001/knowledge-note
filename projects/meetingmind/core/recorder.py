"""
音频录制模块
"""
import wave
import pyaudio
import threading
import signal
import sys


class AudioRecorder:
    """音频录制器"""
    
    def __init__(self, 
                 format=pyaudio.paInt16,
                 channels=1,
                 rate=16000,
                 chunk=1024):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.recording = False
        self.frames = []
        
    def record_until_stop(self, output_file=None) -> str:
        """
        录制直到用户按下Ctrl+C
        
        Returns:
            录音文件路径
        """
        import tempfile
        
        if output_file is None:
            output_file = tempfile.mktemp(suffix='.wav')
        
        self.frames = []
        self.recording = True
        
        # 设置Ctrl+C处理
        def signal_handler(sig, frame):
            print("\n⏹️  停止录音...")
            self.recording = False
        
        original_handler = signal.signal(signal.SIGINT, signal_handler)
        
        try:
            p = pyaudio.PyAudio()
            
            # 打开输入流 (虚拟音频设备)
            # 注意: 需要设置默认输入设备为虚拟音频设备
            stream = p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎤 正在录制...")
            
            while self.recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    print(f"⚠️ 录音错误: {e}")
                    break
            
            # 停止和关闭流
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # 保存WAV文件
            if self.frames:
                with wave.open(output_file, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(p.get_sample_size(self.format))
                    wf.setframerate(self.rate)
                    wf.writeframes(b''.join(self.frames))
                
                duration = len(self.frames) * self.chunk / self.rate
                print(f"💾 录音保存: {output_file} ({duration:.1f}秒)")
                return output_file
            else:
                return None
                
        finally:
            signal.signal(signal.SIGINT, original_handler)
    
    def list_devices(self):
        """列出可用音频设备"""
        p = pyaudio.PyAudio()
        
        print("\n🎧 可用音频输入设备:")
        print("-" * 50)
        
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  [{i}] {info['name']}")
                print(f"      输入通道: {info['maxInputChannels']}")
                print(f"      采样率: {int(info['defaultSampleRate'])}Hz")
        
        p.terminate()
