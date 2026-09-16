import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  PlatformFile? _selectedFile;
  bool _isLoading = false;
  String? _errorMessage;
  String? _successMessage;
  String _recognizedText = '';

  static const double _maxSizeMb = 50;

  Future<void> _pickPdf() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf'],
    );
    if (result == null || result.files.single.path == null) return;

    final picked = result.files.single;
    final sizeMb = picked.size / 1024 / 1024;

    setState(() {
      if (sizeMb > _maxSizeMb) {
        _errorMessage = 'File size should not exceed ${_maxSizeMb.toInt()}MB';
        _successMessage = null;
        _selectedFile = null;
      } else {
        _selectedFile = picked;
        _errorMessage = null;
        _successMessage = null;
        _recognizedText = '';
      }
    });
  }

  void _removeFile() {
    setState(() {
      _selectedFile = null;
      _recognizedText = '';
      _errorMessage = null;
      _successMessage = null;
    });
  }

  void _onRecognizePressed() {
    // TODO(step 4/6): replace with context.read<RecognitionBloc>().add(RecognizePressed())
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Recognition logic not wired yet')),
    );
  }

  void _onDownloadPressed() {
    // TODO(step 7+): call POST /api/download-pdf and save/share the file
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Download logic not wired yet')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      backgroundColor: colorScheme.surfaceContainerLowest,
      appBar: AppBar(
        leading: Padding(
          padding: const EdgeInsets.all(8),
          child: Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(Icons.document_scanner_outlined,
                color: colorScheme.primary),
          ),
        ),
        title: const Text('InkScan'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const _HeaderBlurb(),
              const SizedBox(height: 20),
              _selectedFile == null
                  ? _UploadArea(onTap: _isLoading ? null : _pickPdf)
                  : _FilePreviewCard(
                file: _selectedFile!,
                onRemove: _isLoading ? null : _removeFile,
              ),
              if (_selectedFile != null) ...[
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: _isLoading ? null : _onRecognizePressed,
                  icon: _isLoading
                      ? const SizedBox(
                    height: 18,
                    width: 18,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                      : const Icon(Icons.description_outlined),
                  label: Text(
                    _isLoading ? 'Processing PDF...' : 'Recognize Text from PDF',
                  ),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ],
              if (_errorMessage != null) ...[
                const SizedBox(height: 16),
                _MessageBanner(
                  text: _errorMessage!,
                  icon: Icons.error_outline,
                  color: Colors.red,
                ),
              ],
              if (_successMessage != null) ...[
                const SizedBox(height: 16),
                _MessageBanner(
                  text: _successMessage!,
                  icon: Icons.check_circle_outline,
                  color: Colors.green,
                ),
              ],
              if (_recognizedText.isNotEmpty) ...[
                const SizedBox(height: 24),
                _ResultsSection(
                  text: _recognizedText,
                  onDownload: _onDownloadPressed,
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _HeaderBlurb extends StatelessWidget {
  const _HeaderBlurb();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Icon(Icons.description_outlined, size: 40, color: colorScheme.primary),
        const SizedBox(height: 8),
        Text(
          'Upload your PDF documents with handwritten content\nand get recognized text instantly',
          textAlign: TextAlign.center,
          style: TextStyle(color: colorScheme.onSurfaceVariant),
        ),
      ],
    );
  }
}

class _UploadArea extends StatelessWidget {
  final VoidCallback? onTap;
  const _UploadArea({required this.onTap});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: colorScheme.primary.withOpacity(0.4),
            width: 1.5,
            style: BorderStyle.solid,
          ),
          color: colorScheme.primaryContainer.withOpacity(0.15),
        ),
        child: Column(
          children: [
            Icon(Icons.upload_file, size: 48, color: colorScheme.primary),
            const SizedBox(height: 12),
            const Text('Tap to choose your PDF file',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16)),
            const SizedBox(height: 12),
            OutlinedButton(
              onPressed: onTap,
              child: const Text('Browse PDF Files'),
            ),
            const SizedBox(height: 8),
            Text(
              'Supported format: PDF only (Max 50MB)',
              style: TextStyle(
                color: colorScheme.onSurfaceVariant,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FilePreviewCard extends StatelessWidget {
  final PlatformFile file;
  final VoidCallback? onRemove;
  const _FilePreviewCard({required this.file, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final sizeMb = (file.size / 1024 / 1024).toStringAsFixed(2);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Icon(Icons.picture_as_pdf_outlined,
                size: 56, color: colorScheme.primary),
            const SizedBox(height: 8),
            Text('PDF Document',
                style: TextStyle(color: colorScheme.onSurfaceVariant)),
            const SizedBox(height: 12),
            Text(
              file.name,
              textAlign: TextAlign.center,
              style: const TextStyle(fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
            Text('$sizeMb MB',
                style: TextStyle(color: colorScheme.onSurfaceVariant)),
            const SizedBox(height: 12),
            TextButton.icon(
              onPressed: onRemove,
              icon: const Icon(Icons.close, size: 18, color: Colors.red),
              label: const Text('Remove', style: TextStyle(color: Colors.red)),
            ),
          ],
        ),
      ),
    );
  }
}

class _MessageBanner extends StatelessWidget {
  final String text;
  final IconData icon;
  final Color color;
  const _MessageBanner({
    required this.text,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Text(text, style: TextStyle(color: color)),
          ),
        ],
      ),
    );
  }
}

class _ResultsSection extends StatelessWidget {
  final String text;
  final VoidCallback onDownload;
  const _ResultsSection({required this.text, required this.onDownload});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Expanded(
                  child: Text('Recognized Text',
                      style: TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16)),
                ),
                TextButton.icon(
                  onPressed: onDownload,
                  icon: const Icon(Icons.download_outlined, size: 18),
                  label: const Text('Download PDF'),
                ),
              ],
            ),
            const Divider(),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: colorScheme.surfaceContainerHighest,
                borderRadius: BorderRadius.circular(8),
              ),
              child: SelectableText(text),
            ),
          ],
        ),
      ),
    );
  }
}