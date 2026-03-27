#!/usr/bin/env swift

import AppKit
import Foundation

struct Config {
    var logFile = "/Users/mattias/kratt/output/demo-logs/live_test_latest.log"
    var titleText = "KRATT KUULIS"
    var hideAfter = 2.5
}

final class NonActivatingPanel: NSPanel {
    override var canBecomeKey: Bool { false }
    override var canBecomeMain: Bool { false }
}

final class OverlayWindowController: NSWindowController {
    private let titleLabel = NSTextField(labelWithString: "")
    private let subtitleLabel = NSTextField(labelWithString: "")
    private let timestampLabel = NSTextField(labelWithString: "")
    private let statusLabel = NSTextField(labelWithString: "")
    private var hideWorkItem: DispatchWorkItem?
    private let timestampFormatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter
    }()

    init(titleText: String, logFile: String) {
        let screenFrame = NSScreen.main?.visibleFrame ?? NSRect(x: 0, y: 0, width: 1440, height: 900)
        let width = min(980.0, screenFrame.width - 120.0)
        let height = 280.0
        let origin = NSPoint(
            x: screenFrame.midX - width / 2.0,
            y: screenFrame.midY - height / 2.0 + 80.0
        )
        let frame = NSRect(origin: origin, size: NSSize(width: width, height: height))

        let panel = NonActivatingPanel(
            contentRect: frame,
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )
        panel.isFloatingPanel = true
        panel.level = .statusBar
        panel.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .transient, .ignoresCycle]
        panel.backgroundColor = .clear
        panel.isOpaque = false
        panel.hasShadow = true
        panel.hidesOnDeactivate = false
        panel.ignoresMouseEvents = true
        panel.animationBehavior = .utilityWindow

        let rootView = NSVisualEffectView(frame: frame)
        rootView.material = .hudWindow
        rootView.blendingMode = .behindWindow
        rootView.state = .active
        rootView.wantsLayer = true
        rootView.layer?.cornerRadius = 26
        rootView.layer?.masksToBounds = true
        rootView.layer?.borderWidth = 1
        rootView.layer?.borderColor = NSColor(calibratedWhite: 1.0, alpha: 0.10).cgColor
        panel.contentView = rootView

        let glow = NSView(frame: .zero)
        glow.translatesAutoresizingMaskIntoConstraints = false
        glow.wantsLayer = true
        glow.layer?.backgroundColor = NSColor(calibratedRed: 0.88, green: 0.20, blue: 0.53, alpha: 0.18).cgColor
        glow.layer?.cornerRadius = 22
        rootView.addSubview(glow)

        let stack = NSStackView()
        stack.orientation = .vertical
        stack.alignment = .centerX
        stack.distribution = .gravityAreas
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        rootView.addSubview(stack)

        titleLabel.stringValue = titleText
        titleLabel.font = NSFont.systemFont(ofSize: 64, weight: .heavy)
        titleLabel.textColor = .white
        titleLabel.alignment = .center
        titleLabel.maximumNumberOfLines = 2
        titleLabel.lineBreakMode = .byWordWrapping

        subtitleLabel.stringValue = ""
        subtitleLabel.font = NSFont.monospacedSystemFont(ofSize: 28, weight: .semibold)
        subtitleLabel.textColor = NSColor(calibratedRed: 0.56, green: 0.88, blue: 0.99, alpha: 1.0)
        subtitleLabel.alignment = .center
        subtitleLabel.maximumNumberOfLines = 2
        subtitleLabel.lineBreakMode = .byTruncatingMiddle

        timestampLabel.stringValue = ""
        timestampLabel.font = NSFont.monospacedDigitSystemFont(ofSize: 18, weight: .medium)
        timestampLabel.textColor = NSColor(calibratedWhite: 1.0, alpha: 0.72)
        timestampLabel.alignment = .center

        statusLabel.stringValue = "Watching \(logFile)   |   press Ctrl+C in terminal to quit"
        statusLabel.font = NSFont.systemFont(ofSize: 14, weight: .medium)
        statusLabel.textColor = NSColor(calibratedWhite: 1.0, alpha: 0.55)
        statusLabel.alignment = .center
        statusLabel.lineBreakMode = .byTruncatingMiddle

        stack.addArrangedSubview(titleLabel)
        stack.addArrangedSubview(subtitleLabel)
        stack.addArrangedSubview(timestampLabel)
        stack.addArrangedSubview(statusLabel)

        NSLayoutConstraint.activate([
            glow.leadingAnchor.constraint(equalTo: rootView.leadingAnchor, constant: 18),
            glow.trailingAnchor.constraint(equalTo: rootView.trailingAnchor, constant: -18),
            glow.topAnchor.constraint(equalTo: rootView.topAnchor, constant: 18),
            glow.bottomAnchor.constraint(equalTo: rootView.bottomAnchor, constant: -18),

            stack.leadingAnchor.constraint(equalTo: rootView.leadingAnchor, constant: 42),
            stack.trailingAnchor.constraint(equalTo: rootView.trailingAnchor, constant: -42),
            stack.centerYAnchor.constraint(equalTo: rootView.centerYAnchor),
        ])

        super.init(window: panel)
        panel.orderOut(nil)
    }

    @available(*, unavailable)
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    func showOverlay(subtitle: String, hideAfter: Double) {
        hideWorkItem?.cancel()

        titleLabel.alphaValue = 0
        subtitleLabel.alphaValue = 0
        timestampLabel.alphaValue = 0
        subtitleLabel.stringValue = subtitle
        timestampLabel.stringValue = timestampFormatter.string(from: Date())

        guard let window else { return }
        window.center()
        window.alphaValue = 0
        window.orderFrontRegardless()

        NSAnimationContext.runAnimationGroup { context in
            context.duration = 0.12
            window.animator().alphaValue = 1
            titleLabel.animator().alphaValue = 1
            subtitleLabel.animator().alphaValue = 1
            timestampLabel.animator().alphaValue = 1
        }

        let workItem = DispatchWorkItem { [weak self] in
            guard let self, let window = self.window else { return }
            NSAnimationContext.runAnimationGroup({ context in
                context.duration = 0.18
                window.animator().alphaValue = 0
            }, completionHandler: {
                window.orderOut(nil)
            })
        }
        hideWorkItem = workItem
        DispatchQueue.main.asyncAfter(deadline: .now() + hideAfter, execute: workItem)
    }
}

final class LogFollower {
    private let logFile: URL
    private let overlay: OverlayWindowController
    private let hideAfter: Double
    private var fileHandle: FileHandle?
    private var currentFileResourceID: Data?
    private var buffer = Data()
    private let pollInterval: TimeInterval = 0.10
    private let detectionRegex = try! NSRegularExpression(
        pattern: #">>> DETECTED (.+?)! \(prob=([0-9.]+), count=([0-9]+)\) <<<"#,
        options: []
    )

    init(logFile: String, overlay: OverlayWindowController, hideAfter: Double) {
        self.logFile = URL(fileURLWithPath: logFile)
        self.overlay = overlay
        self.hideAfter = hideAfter
    }

    func start() {
        poll()
    }

    private func resolvedURL() -> URL {
        logFile.resolvingSymlinksInPath()
    }

    private func fileResourceID(for url: URL) -> Data? {
        try? url.resourceValues(forKeys: [.fileResourceIdentifierKey]).fileResourceIdentifier as? Data
    }

    private func reopenIfNeeded() {
        let resolved = resolvedURL()
        guard FileManager.default.fileExists(atPath: resolved.path) else { return }

        let resourceID = fileResourceID(for: resolved)
        if fileHandle == nil || resourceID != currentFileResourceID {
            try? fileHandle?.close()
            fileHandle = try? FileHandle(forReadingFrom: resolved)
            currentFileResourceID = resourceID
            if let fh = fileHandle {
                try? fh.seekToEnd()
            }
            buffer.removeAll(keepingCapacity: true)
        }
    }

    private func poll() {
        reopenIfNeeded()

        if let fh = fileHandle, let data = try? fh.readToEnd(), !data.isEmpty {
            buffer.append(data)
            while let newlineRange = buffer.firstRange(of: Data([0x0a])) {
                let lineData = buffer.subdata(in: 0..<newlineRange.lowerBound)
                buffer.removeSubrange(0...newlineRange.lowerBound)
                if let line = String(data: lineData, encoding: .utf8) {
                    handle(line: line)
                }
            }
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + pollInterval) { [weak self] in
            self?.poll()
        }
    }

    private func handle(line: String) {
        guard line.contains(">>> DETECTED ") else { return }
        let nsLine = line as NSString
        let range = NSRange(location: 0, length: nsLine.length)
        if let match = detectionRegex.firstMatch(in: line, options: [], range: range) {
            let name = nsLine.substring(with: match.range(at: 1))
            let probability = nsLine.substring(with: match.range(at: 2))
            let count = nsLine.substring(with: match.range(at: 3))
            let subtitle = "\(name)   |   p=\(probability)   |   count=\(count)"
            overlay.showOverlay(subtitle: subtitle, hideAfter: hideAfter)
        } else {
            overlay.showOverlay(subtitle: line, hideAfter: hideAfter)
        }
    }
}

func parseArgs() -> Config {
    var config = Config()
    var iterator = CommandLine.arguments.dropFirst().makeIterator()

    while let arg = iterator.next() {
        switch arg {
        case "--log-file":
            if let value = iterator.next() { config.logFile = value }
        case "--text":
            if let value = iterator.next() { config.titleText = value }
        case "--hide-after":
            if let value = iterator.next(), let seconds = Double(value) { config.hideAfter = seconds }
        case "-h", "--help":
            print("""
            usage: kratt_detection_overlay.swift [--log-file PATH] [--text MESSAGE] [--hide-after SECONDS]

              --log-file    Log file to follow. Default: \(config.logFile)
              --text        Main overlay text. Default: \(config.titleText)
              --hide-after  Seconds to keep overlay visible. Default: \(config.hideAfter)
            """)
            exit(0)
        default:
            continue
        }
    }
    return config
}

let config = parseArgs()

let app = NSApplication.shared
app.setActivationPolicy(.accessory)

let overlay = OverlayWindowController(titleText: config.titleText, logFile: config.logFile)
let follower = LogFollower(logFile: config.logFile, overlay: overlay, hideAfter: config.hideAfter)
follower.start()
app.run()
