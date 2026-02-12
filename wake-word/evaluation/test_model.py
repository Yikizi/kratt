#!/usr/bin/env python3
"""
Testi wake word mudelit ja leia optimaalne threshold.
"""

import argparse
import numpy as np
from pathlib import Path
from sklearn.metrics import roc_curve, auc, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from openwakeword import Model
    HAS_OPENWAKEWORD = True
except ImportError:
    HAS_OPENWAKEWORD = False
    print("⚠️  openwakeword ei ole installitud")

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    print("⚠️  soundfile ei ole installitud")

try:
    import tensorflow as tf
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    print("⚠️  tensorflow ei ole installitud")

def load_audio(file_path, target_sr=16000):
    """Laadi audio fail."""
    if not HAS_SOUNDFILE:
        raise ImportError("soundfile on vajalik: pip install soundfile")
    audio, sr = sf.read(file_path)
    if sr != target_sr:
        # Simple resample (for testing only, use librosa for production)
        audio = np.interp(
            np.linspace(0, len(audio), int(len(audio) * target_sr / sr)),
            np.arange(len(audio)),
            audio
        )
    return audio

def test_openwakeword(model_path, positive_dir, negative_dir):
    """Testi openWakeWord mudelit."""
    if not HAS_OPENWAKEWORD:
        print("❌ Installi openwakeword: pip install openwakeword")
        return

    print(f"📊 Testin openWakeWord mudelit: {model_path}")

    # Laadi mudel
    model_name = Path(model_path).stem
    model = Model(wakeword_models=[model_path])

    # Test positive samples
    y_true = []
    y_scores = []

    print("\n🟢 Testin positive samples...")
    positive_files = list(Path(positive_dir).glob("*.wav"))
    for i, audio_file in enumerate(positive_files):
        if i % 10 == 0:
            print(f"   {i}/{len(positive_files)}", end='\r')

        audio = load_audio(audio_file)
        prediction = model.predict(audio)
        score = prediction.get(model_name, 0.0)

        y_true.append(1)
        y_scores.append(score)

    print(f"   {len(positive_files)}/{len(positive_files)} ✅")

    # Test negative samples
    print("\n🔴 Testin negative samples...")
    negative_files = list(Path(negative_dir).glob("*.wav"))[:len(positive_files)]  # Same amount
    for i, audio_file in enumerate(negative_files):
        if i % 10 == 0:
            print(f"   {i}/{len(negative_files)}", end='\r')

        audio = load_audio(audio_file)
        prediction = model.predict(audio)
        score = prediction.get(model_name, 0.0)

        y_true.append(0)
        y_scores.append(score)

    print(f"   {len(negative_files)}/{len(negative_files)} ✅")

    # Analyze results
    analyze_results(y_true, y_scores, model_name)

def test_tflite(model_path, positive_dir, negative_dir):
    """Testi TFLite mudelit (microWakeWord)."""
    if not HAS_TENSORFLOW:
        print("❌ Installi tensorflow: pip install tensorflow")
        return

    print(f"📊 Testin TFLite mudelit: {model_path}")

    # Laadi TFLite mudel
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"   Input shape: {input_details[0]['shape']}")
    print(f"   Output shape: {output_details[0]['shape']}")

    # Test samples
    y_true = []
    y_scores = []

    def predict_audio(audio_file):
        """Ennusta ühe audio faili jaoks."""
        audio = load_audio(audio_file)

        # Prepare input (adjust based on your model's expected input)
        # This is a simplified version - adjust for your specific model
        input_shape = input_details[0]['shape']
        if len(input_shape) == 2:  # [batch, samples]
            audio_input = audio[:input_shape[1]].reshape(1, -1)
        elif len(input_shape) == 3:  # [batch, time_steps, features]
            # Compute spectrogram or MFCC features here
            # This is model-specific!
            audio_input = np.zeros(input_shape)  # Placeholder
        else:
            raise ValueError(f"Unexpected input shape: {input_shape}")

        # Quantize if INT8
        if input_details[0]['dtype'] == np.int8:
            scale, zero_point = input_details[0]['quantization']
            audio_input = (audio_input / scale + zero_point).astype(np.int8)

        interpreter.set_tensor(input_details[0]['index'], audio_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

        # Dequantize if INT8
        if output_details[0]['dtype'] == np.int8:
            scale, zero_point = output_details[0]['quantization']
            output = (output.astype(np.float32) - zero_point) * scale

        return float(output[0])

    # Test positive
    print("\n🟢 Testin positive samples...")
    positive_files = list(Path(positive_dir).glob("*.wav"))
    for i, audio_file in enumerate(positive_files):
        if i % 10 == 0:
            print(f"   {i}/{len(positive_files)}", end='\r')
        try:
            score = predict_audio(audio_file)
            y_true.append(1)
            y_scores.append(score)
        except Exception as e:
            print(f"\n⚠️  Viga failiga {audio_file.name}: {e}")

    print(f"   {len([x for x in y_true if x == 1])}/{len(positive_files)} ✅")

    # Test negative
    print("\n🔴 Testin negative samples...")
    negative_files = list(Path(negative_dir).glob("*.wav"))[:len(positive_files)]
    for i, audio_file in enumerate(negative_files):
        if i % 10 == 0:
            print(f"   {i}/{len(negative_files)}", end='\r')
        try:
            score = predict_audio(audio_file)
            y_true.append(0)
            y_scores.append(score)
        except Exception as e:
            print(f"\n⚠️  Viga failiga {audio_file.name}: {e}")

    print(f"   {len([x for x in y_true if x == 0])}/{len(negative_files)} ✅")

    # Analyze
    model_name = Path(model_path).stem
    analyze_results(y_true, y_scores, model_name)

def analyze_results(y_true, y_scores, model_name):
    """Analüüsi tulemusi ja leia optimaalne threshold."""
    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    print("\n" + "="*60)
    print("📊 RESULTS ANALYSIS")
    print("="*60)

    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)

    print(f"\n🎯 AUC Score: {roc_auc:.3f}")

    # Find optimal threshold (maximize TPR - FPR)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]

    print(f"🎚️  Optimal Threshold: {optimal_threshold:.3f}")
    print(f"   TPR (True Positive Rate): {tpr[optimal_idx]:.3f}")
    print(f"   FPR (False Positive Rate): {fpr[optimal_idx]:.3f}")

    # Test different thresholds
    print("\n📈 Different Thresholds:")
    print("   Threshold | TPR   | FPR   | Accuracy")
    print("   " + "-"*45)

    for threshold in [0.3, 0.4, 0.5, 0.6, 0.7]:
        y_pred = (y_scores >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        tpr_at_thresh = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr_at_thresh = fp / (fp + tn) if (fp + tn) > 0 else 0
        accuracy = (tp + tn) / len(y_true)

        marker = " ⭐" if abs(threshold - optimal_threshold) < 0.05 else ""
        print(f"   {threshold:.1f}       | {tpr_at_thresh:.3f} | {fpr_at_thresh:.3f} | {accuracy:.3f}{marker}")

    # Confusion matrix at optimal threshold
    y_pred_optimal = (y_scores >= optimal_threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred_optimal)

    print("\n🎯 Confusion Matrix (at optimal threshold):")
    print("              Predicted")
    print("              Neg    Pos")
    print(f"   Actual Neg {cm[0,0]:4d}   {cm[0,1]:4d}")
    print(f"   Actual Pos {cm[1,0]:4d}   {cm[1,1]:4d}")

    # Plot ROC curve
    try:
        plt.figure(figsize=(10, 5))

        # ROC Curve
        plt.subplot(1, 2, 1)
        plt.plot(fpr, tpr, 'b-', label=f'ROC (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], 'r--', label='Random')
        plt.plot(fpr[optimal_idx], tpr[optimal_idx], 'go', markersize=10,
                label=f'Optimal (threshold={optimal_threshold:.3f})')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Score distribution
        plt.subplot(1, 2, 2)
        plt.hist(y_scores[y_true == 0], bins=50, alpha=0.5, label='Negative', color='red')
        plt.hist(y_scores[y_true == 1], bins=50, alpha=0.5, label='Positive', color='green')
        plt.axvline(optimal_threshold, color='black', linestyle='--',
                   label=f'Optimal threshold ({optimal_threshold:.3f})')
        plt.xlabel('Prediction Score')
        plt.ylabel('Count')
        plt.title('Score Distribution')
        plt.legend()
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        output_file = f'{model_name}_analysis.png'
        plt.savefig(output_file, dpi=150)
        print(f"\n📊 Plot salvestatud: {output_file}")

    except Exception as e:
        print(f"\n⚠️  Plotti ei õnnestunud luua: {e}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    print(f"   1. Kasuta threshold: {optimal_threshold:.3f}")
    print(f"   2. Expected TPR: {tpr[optimal_idx]*100:.1f}% (detects correct wake words)")
    print(f"   3. Expected FPR: {fpr[optimal_idx]*100:.1f}% (false alarms)")

    if fpr[optimal_idx] > 0.05:
        print(f"   ⚠️  FPR is high! Consider:")
        print(f"      - Add more negative samples")
        print(f"      - Retrain with more diverse data")
    if tpr[optimal_idx] < 0.90:
        print(f"   ⚠️  TPR is low! Consider:")
        print(f"      - Add more positive samples")
        print(f"      - Lower threshold (more false alarms)")

def main():
    parser = argparse.ArgumentParser(description='Test wake word model')
    parser.add_argument('--model', type=str, required=True, help='Model path (.onnx or .tflite)')
    parser.add_argument('--positive-dir', type=str, default='data/positive',
                       help='Positive test samples directory')
    parser.add_argument('--negative-dir', type=str, default='data/negative_samples',
                       help='Negative test samples directory')

    args = parser.parse_args()

    model_path = Path(args.model)
    if not model_path.exists():
        print(f"❌ Mudelit ei leitud: {model_path}")
        return

    # Detect model type
    if model_path.suffix == '.tflite':
        test_tflite(str(model_path), args.positive_dir, args.negative_dir)
    elif model_path.suffix in ['.onnx', '.pkl']:
        test_openwakeword(str(model_path), args.positive_dir, args.negative_dir)
    else:
        print(f"❌ Unknown model format: {model_path.suffix}")
        print("   Supported: .tflite (microWakeWord), .onnx/.pkl (openWakeWord)")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test katkestatud")
    except Exception as e:
        print(f"\n\n❌ Viga: {e}")
        import traceback
        traceback.print_exc()
