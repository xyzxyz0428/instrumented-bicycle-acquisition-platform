import smbus
import time

I2C_BUS = 1
I2C_ADDR = 0x24
# Lista de registradores comuns para canais analógicos
CHANNELS = {
    "CH0": 0x10, "CH1": 0x11, "CH2": 0x12, "CH3": 0x13,
    "CH4": 0x14, "CH5": 0x15, "CH6": 0x16, "CH7": 0x17
}

bus = smbus.SMBus(I2C_BUS)

print("--- Scanner de Portas Analógicas ---")
print("Pressione o sensor para identificar a porta ativa.\n")

try:
    while True:
        results = []
        for name, reg in CHANNELS.items():
            try:
                # Lê o valor bruto (raw) de cada registrador
                bus.write_byte(I2C_ADDR, reg)
                val = bus.read_word_data(I2C_ADDR, reg)
                results.append(f"{name}: {val:5}")
            except:
                results.append(f"{name}: ERR  ")
        
        # Imprime todos na mesma linha para facilitar a comparação
        print(" | ".join(results), end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\nScanner finalizado.")
